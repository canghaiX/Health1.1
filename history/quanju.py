# 检查retrieval返回数据的格式是什么样的，87行用到了返回的格式用到了[{"content":"xxx","score":0.x}]的格式
# _update_llm_responses这个函数只记录了模型的回复，而忽略了用户的问题。
# _cleanup中为什么要向客户端发送总结内容？

import asyncio
from datetime import datetime
from uuid import uuid4
import json
from starlette.websockets import WebSocketState

from fastapi import WebSocket, status
from sqlalchemy.orm import Session
from typing import List
from starlette.websockets import WebSocketDisconnect  # 正确导入断开异常
from app.models.conversation_model import ConversationSummary
from app.routers.rag_knowledge import retrieval
from app.utils.llm_client import get_llm_response  # LLM调用函数（需处理异常）
from openai import AsyncOpenAI

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ConversationService:
    def __init__(self):
        self.conversation_history: List[str] = []
        self.conversation_id_kb: dict[str, str] = {}
        # 仅新增这两行初始化本地模型
        self.tokenizer = AutoTokenizer.from_pretrained(
            "/home/hsap/hsap_model/DeepSeek-R1-Distill-Qwen-32B",
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            "/home/hsap/hsap_model/DeepSeek-R1-Distill-Qwen-32B",
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True
        )

    async def _call_llm(self, prompt: str) -> str:
        """唯一需要修改的方法：替换OpenAI调用为本地模型"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.7
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 以下所有方法保持原样，完全不变 ▼▼▼
    def bind_conversation_kb(self, conversation_id: str, conversation_kb: str):
        self.conversation_id_kb[conversation_id] = conversation_kb

    def get_kb_by_id(self, conversation_id: str):
        return self.conversation_id_kb[conversation_id]

    async def retrieve_knowledge(self, query: str, kb_id: str, db: Session) -> list:
        retrieval_result = retrieval(kbId=kb_id, query=query, limit=3)
        if retrieval_result["code"] != 200:
            return []
        return [{"content": doc["content"], "score": doc["score"]} for doc in retrieval_result["files"]]

    @staticmethod
    def create_conversation_id() -> str:
        return str(uuid4())

    async def handle_conversation_flow(
            self,
            websocket: WebSocket,
            conversation_id: str,
            user_id: str,
            db: Session,
            kb_id: str
    ):
        self.websocket = websocket
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.db = db
        self.kb_id = kb_id

        await websocket.accept()
        print("websocket连接已接受")
        try:
            while True:
                user_message = await self._receive_with_timeout()
                print(f"{user_message},这是接收到的用户输入")
                try:
                    query = user_message
                    if not query:
                        await websocket.send_json({"error": "问题不能为空"})
                except (json.JSONDecodeError, KeyError):
                    await websocket.send_json({"error": "无效的消息格式"})
                    continue

                context_docs = await self.retrieve_knowledge(query, kb_id, db)
                print(f"检索到的文档: {context_docs}")

                if context_docs:
                    context_prompt = "以下是与你的问题相关的知识库内容：\n"
                    for i, doc in enumerate(context_docs, 1):
                        context_prompt += f"{i}. {doc['content']}\n"
                    context_prompt += "请根据以上内容，结合你的知识，回答用户的问题："
                else:
                    context_prompt = "未找到相关知识库内容，请直接回答用户的问题："
                full_prompt = f"{context_prompt}\n用户问题：{query},请一定注意你的身份是惠斯安普公司开发的健康助手，能够对健康相关问题进行恰当回复"

                llm_response = await self._call_llm(full_prompt)
                print(f"LLM回复: {llm_response}")

                self._update_llm_responses(llm_response)
                await websocket.send_text(llm_response)

        except (asyncio.TimeoutError, WebSocketDisconnect) as e:
            reason = "用户超时未输入" if isinstance(e, asyncio.TimeoutError) else "客户端断开"
            await self._cleanup(reason)
        except Exception as e:
            print(f"发生异常: {str(e)}")
            await self._cleanup(f"系统错误：{str(e)}")

    async def _receive_with_timeout(self) -> str:
        try:
            return await asyncio.wait_for(
                self.websocket.receive_text(),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            raise

    def _update_llm_responses(self, llm_response: str):
        self.conversation_history.append(llm_response)

    async def _cleanup(self, reason: str):
        try:
            summary = await self._generate_summary()
            self._save_summary_to_db(summary)
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_text(f"总结：{summary}")
                await self.websocket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason=short_reason[:100]
                )
                self.db.close()
        except Exception as e:
            self.db.close()
            await self.websocket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"系统错误，请重试{e}"[:100]
            )

    async def _generate_summary(self) -> str:
        if not self.conversation_history:
            return "无有效对话内容"
        history_content = "\n".join([f"{msg}" for msg in self.conversation_history])
        prompt = f"""请用简洁的中文总结以下LLM的回复内容：
        {history_content}"""
        return await self._call_llm(prompt)

    def _save_summary_to_db(self, summary: str):
        try:
            db_summary = ConversationSummary(
                uuid=self.conversation_id,
                summary=summary,
                user_id=self.user_id,
                create_time=datetime.now()
            )
            self.db.add(db_summary)
            self.db.commit()
            self.db.refresh(db_summary)
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"数据库写入失败：{str(e)}")

    async def talk_api_numberPeople(self, input: str):
        prompt = f"""你现在的身份是惠斯安普公司开发的医疗助手大模型，能够根据病人情况给出身体健康建议。给出的建议要是口语化文本，能直接读出来，不要带有逗号句号以外的标点符号，不要用markdown标记。用户问题：{input}"""
        return await self._call_llm(prompt)
