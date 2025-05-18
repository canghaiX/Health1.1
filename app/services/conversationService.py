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


class ConversationService:
    conversation_id_kb: dict[str, str] = {}  # 存id与kb的映射

    def __init__(self):
        self.conversation_history: List[str] = []  # 仅存储LLM回复

    def bind_conversation_kb(self, conversation_id: str, conversation_kb: str):
        self.conversation_id_kb[conversation_id] = conversation_kb

    def get_kb_by_id(self, conversation_id: str):
        return self.conversation_id_kb[conversation_id]

    async def retrieve_knowledge(self, query: str, kb_id: str, db: Session) -> list:
        """
        调用知识库检索接口，获取与问题相关的上下文
        :param query: 用户问题
        :param kb_id: 知识库ID（需由前端或会话关联）
        :param db: 数据库会话（若需要）
        :return: 检索到的文档列表（如 [{"content": "文档内容", "score": 0.8}, ...]）
        """
        # 调用知识库检索接口（假设返回格式为 {"code": 200, "files": [...]}}）
        retrieval_result = retrieval(kbId=kb_id, query=query, limit=3)  # limit=3 取前3条
        if retrieval_result["code"] != 200:
            return []  # 检索失败返回空列表
        # 提取文档内容（样例，此处还需调整）
        return [{"content": doc["content"], "score": doc["score"]} for doc in retrieval_result["files"]]

    @staticmethod
    def create_conversation_id() -> str:
        """生成唯一会话ID（UUID）"""
        return str(uuid4())

    async def handle_conversation_flow(
            self,
            websocket: WebSocket,
            conversation_id: str,
            user_id: str,
            db: Session,
            kb_id: str  # 关联知识库
    ):
        """处理完整对话流程（含超时和总结逻辑）"""
        self.websocket = websocket
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.db = db
        self.kb_id = kb_id

        await websocket.accept()  # 接受WebSocket连接

        try:
            while True:
                # 带10秒超时的消息接收（用户输入）
                user_message = await self._receive_with_timeout()
                try:
                    user_message = json.loads(user_message)
                    query = user_message["query"]
                    if not query:
                        await websocket.send_json({"error": "问题不能为空"})
                except (json.JSONDecodeError, KeyError):
                    await websocket.send_json({"error": "无效的消息格式"})
                    continue
                # 接入rag 调用检索模块获取上下文
                context_docs = await self.retrieve_knowledge(query, kb_id, db)
                print(f"检索到的文档: {context_docs}")  # 添加调试信息

                # 构造prompt
                if context_docs:
                    context_prompt = "以下是与你的问题相关的知识库内容：\n"
                    for i, doc in enumerate(context_docs, 1):
                        context_prompt += f"{i}. {doc['content']}\n"
                    context_prompt += "请根据以上内容，结合你的知识，回答用户的问题："
                else:
                    context_prompt = "未找到相关知识库内容，请直接回答用户的问题："
                full_prompt = f"{context_prompt}\n用户问题：{query}"

                # 调用LLM获取回复（异步包装）
                llm_response = await self._call_llm(full_prompt)
                print(f"LLM回复: {llm_response}")  # 添加调试信息

                # 记录LLM回复到历史（关键：仅存储LLM回复）
                self._update_llm_responses(llm_response)

                # 发送LLM回复给前端
                await websocket.send_text(llm_response)

        except (asyncio.TimeoutError, WebSocketDisconnect) as e:
            # 超时或主动断开时触发清理
            reason = "用户超时未输入" if isinstance(e, asyncio.TimeoutError) else "客户端断开"
            await self._cleanup(reason)

        except Exception as e:
            # 其他异常处理（如LLM调用失败）
            print(f"发生异常: {str(e)}")  # 添加调试信息
            await self._cleanup(f"系统错误：{str(e)}")

    async def _receive_with_timeout(self) -> str:
        """带10秒超时的消息接收"""
        try:
            return await asyncio.wait_for(
                self.websocket.receive_text(),
                timeout=10.0  # 超时时间：10秒
            )
        except asyncio.TimeoutError:
            raise  # 抛给外层处理

    async def _call_llm(self, user_message: str) -> str:
        """异步调用LLM（带异常处理）"""
        try:
            # 同步函数转异步（使用线程池避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, get_llm_response, user_message)
        except Exception as e:
            # 记录异常信息
            import logging
            logging.error(f"LLM调用失败：{str(e)}")
            raise RuntimeError(f"LLM调用失败：{str(e)}")

    def _update_llm_responses(self, llm_response: str):
        """记录LLM回复到内存列表（仅存储回复内容）"""
        self.conversation_history.append(llm_response)

    async def _cleanup(self, reason: str):
        try:

            summary = await self._generate_summary()
            self._save_summary_to_db(summary)

            # 1. 先发送总结消息（通过普通消息通道）
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_text(f"总结：{summary}")

            # 2. 再关闭连接（原因字段控制在123字节内）
            short_reason = f"对话结束（原因：{reason[:100]}）"  # 截断原因至100字节
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason=short_reason[:100]  # 确保不超过123字节
                )
                # 关闭数据库会话
                self.db.close()

        except Exception as e:
            # 关闭数据库会话
            self.db.close()
            await self.websocket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"系统错误，请重试{e}"[:100] 
            )

    async def _generate_summary(self) -> str:
        """基于LLM历史回复生成总结（调用LLM）"""
        if not self.conversation_history:
            return "无有效对话内容"

        # 构造总结提示词（拼接LLM历史回复）
        history_content = "\n".join([f"{msg}" for msg in self.conversation_history])
        prompt = f"""请用简洁的中文总结以下LLM的回复内容：
        {history_content}"""

        # 调用LLM生成总结（异步处理）
        return await self._call_llm(prompt)  # 复用LLM调用逻辑

    def _save_summary_to_db(self, summary: str):
        """写入总结到数据库（带事务控制）"""
        try:
            db_summary = ConversationSummary(
                uuid=self.conversation_id,
                summary=summary,
                user_id=self.user_id,
                create_time=datetime.now()
            )
            self.db.add(db_summary)
            self.db.commit()  # 提交事务
            self.db.refresh(db_summary)  # 可选：刷新对象获取数据库生成的字段
        except Exception as e:
            self.db.rollback()  # 异常时回滚
            raise RuntimeError(f"数据库写入失败：{str(e)}")
