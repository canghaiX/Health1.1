import uuid
import threading
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from openai import OpenAI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from app.config import Configuration
import openai

'''
这里调用的豆包的服务，后续还要进行修改
'''
# ========== 集中配置区域 ==========
ARK_API_KEY = "doubao api key"
if not ARK_API_KEY:
    raise ValueError(
        "ARK_API_KEY 未设置！请通过环境变量配置，示例：\n"
        "Linux/macOS: export ARK_API_KEY='your_key'\n"
        "Windows: set ARK_API_KEY=your_key"
    )
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DOUBA_MODEL = "doubao-1-5-thinking-pro-250415"
TIMEOUT_SECONDS = 10
SUMMARY_PROMPT = "请用一句话总结以下对话内容："

# ========== 数据模型定义 ==========
class MessageRequest(BaseModel):
    message: str = Field(..., description="用户输入的消息内容")

class MessageResponse(BaseModel):
    reply: str = Field(..., description="模型生成的回复")
    conversation_id: str = Field(..., description="会话ID")
    status: str = Field(..., description="会话状态：active/timeout_warning/ended")
    summary: Optional[str] = Field(None, description="对话总结（结束时返回）")

class ConversationStatus:
    ACTIVE = "active"
    TIMEOUT_WARNING = "timeout_warning"
    ENDED = "ended"

# ========== 会话核心类 ==========
class Conversation:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.messages: List[str] = []
        self.status = ConversationStatus.ACTIVE
        self.timer: Optional[threading.Timer] = None

client = OpenAI(
    base_url=ARK_BASE_URL,
    api_key=ARK_API_KEY
)

# ========== 会话管理器 ==========
class ConversationManager:
    def __init__(self, main_loop: asyncio.AbstractEventLoop):
        self.main_loop = main_loop
        self.conversations: Dict[str, Conversation] = {}
        self.websockets: Dict[str, WebSocket] = {}

    def create_conversation(self) -> Conversation:
        conv = Conversation()
        self.conversations[conv.id] = conv
        return conv

    def _get_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.conversations:
            raise HTTPException(404, "会话不存在")
        return self.conversations[conversation_id]

    def _reset_timer(self, conversation_id: str) -> None:
        conv = self._get_conversation(conversation_id)
        if conv.timer:
            conv.timer.cancel()
        conv.timer = threading.Timer(
            TIMEOUT_SECONDS, self._handle_timeout, [conversation_id]
        )
        conv.timer.daemon = True
        conv.timer.start()

    def _handle_timeout(self, conversation_id: str) -> None:
        conv = self._get_conversation(conversation_id)
        if conv.status == ConversationStatus.ACTIVE:
            conv.status = ConversationStatus.TIMEOUT_WARNING
            self._send_warning(conversation_id)
            conv.timer = threading.Timer(
                TIMEOUT_SECONDS, self._end_conversation, [conversation_id, True]
            )
            conv.timer.daemon = True
            conv.timer.start()

    def _send_warning(self, conversation_id: str) -> None:
        ws = self.websockets.get(conversation_id)
        if not ws:
            return
        response = MessageResponse(
            reply="长时间未输入，对话将在10秒后结束。输入'结束'可立即终止对话",
            conversation_id=conversation_id,
            status=ConversationStatus.TIMEOUT_WARNING
        )
        asyncio.run_coroutine_threadsafe(
            self._send_websocket_message(ws, response), self.main_loop
        )

    def _end_conversation(self, conversation_id: str, auto_end: bool = False) -> None:
        if conversation_id not in self.conversations:
            return
        conv = self._get_conversation(conversation_id)
        summary = self._generate_summary(conv.messages) if auto_end else None
        response = MessageResponse(
            reply="对话已结束" + (f"，总结：{summary}" if summary else ""),
            conversation_id=conversation_id,
            status=ConversationStatus.ENDED,
            summary=summary
        )

        ws = self.websockets.pop(conversation_id, None)
        if not ws:
            del self.conversations[conversation_id]
            return

        async def safe_close():
            try:
                if ws.client_state == "connected":
                    await self._send_websocket_message(ws, response)
                await ws.close()
            except Exception as e:
                print(f"关闭连接异常: {e}")

        asyncio.run_coroutine_threadsafe(safe_close(), self.main_loop)

        if conv.timer:
            conv.timer.cancel()
        del self.conversations[conversation_id]

    def _generate_summary(self, messages: List[str]) -> str:
        if not messages:
            return "无对话内容"
        recent_messages = messages[-50:]
        prompt = f"{SUMMARY_PROMPT}\n{''.join(recent_messages)}"
        try:
            response = client.chat.completions.create(
                model=DOUBA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"总结生成失败: {e}")
            return "总结生成失败"

    def handle_message(self, conversation_id: str, message: str) -> MessageResponse:
        conv = self._get_conversation(conversation_id)
        if conv.status == ConversationStatus.TIMEOUT_WARNING:
            if message.strip().lower() in ["结束", "exit", "quit"]:
                self._end_conversation(conversation_id, auto_end=False)
                return MessageResponse(
                    reply="对话已手动结束",
                    conversation_id=conversation_id,
                    status=ConversationStatus.ENDED,
                    summary=self._generate_summary(conv.messages)
                )
            conv.status = ConversationStatus.ACTIVE
        self._reset_timer(conversation_id)
        conv.messages.append(f"用户：{message}")
        try:
            reply = self._call_douba_through_ark(message)
            conv.messages.append(f"助手：{reply}")
        except Exception as e:
            raise HTTPException(500, f"模型调用失败: {e}")
        return MessageResponse(
            reply=reply,
            conversation_id=conversation_id,
            status=conv.status
        )

    def _call_douba_through_ark(self, prompt: str) -> str:
        try:
            response = client.chat.completions.create(
                model=DOUBA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.8,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except openai.OpenAIError as e:
            raise HTTPException(500, f"方舟API错误: {e.error.message}")
        except Exception as e:
            raise HTTPException(500, f"模型调用失败: {e}")

    @staticmethod
    async def _send_websocket_message(websocket: WebSocket, response: MessageResponse) -> None:
        try:
            await websocket.send_json(response.model_dump())
        except Exception as e:
            if "close message has been sent" in str(e):
                pass
            else:
                print(f"消息发送失败: {e}")

# ========== 应用生命周期与依赖注入 ==========
class AppState:
    def __init__(self, main_loop: asyncio.AbstractEventLoop):
        self.conversation_manager = ConversationManager(main_loop)

@asynccontextmanager
async def lifespan(app: FastAPI):
    main_loop = asyncio.get_running_loop()
    app.state = AppState(main_loop)
    yield
    for conv_id in list(app.state.conversation_manager.conversations.keys()):
        app.state.conversation_manager._end_conversation(conv_id)

app = FastAPI(title="豆包智能对话服务", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conversation_manager():
    if not hasattr(app.state, "conversation_manager"):
        raise HTTPException(503, "服务未初始化")
    return app.state.conversation_manager

@app.post("/conversations/", response_model=MessageResponse)
def create_conversation(
    conversation_manager: ConversationManager = Depends(get_conversation_manager)
):
    conv = conversation_manager.create_conversation()
    return MessageResponse(
        reply="新会话创建成功，请开始对话",
        conversation_id=conv.id,
        status=ConversationStatus.ACTIVE
    )

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    conversation_manager: ConversationManager = Depends(get_conversation_manager)
):
    await websocket.accept()
    try:
        conversation_manager._get_conversation(conversation_id)
        conversation_manager.websockets[conversation_id] = websocket
        conversation_manager._reset_timer(conversation_id)
        while True:
            data = await websocket.receive_json()
            response = conversation_manager.handle_message(conversation_id, data["message"])
            await conversation_manager._send_websocket_message(websocket, response)
            if response.status == ConversationStatus.ENDED:
                break
    except WebSocketDisconnect:
        print(f"客户端{conversation_id}主动断开连接")
    except HTTPException as e:
        await websocket.send_text(f"错误: {e.detail}")
    finally:
        if conversation_id in conversation_manager.websockets:
            del conversation_manager.websockets[conversation_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)