from fastapi import APIRouter, WebSocket, Depends, status,FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.conversationService import ConversationService
from app.models.conversation_model import get_db

app = FastAPI(title="HRA报告解读服务")
conversation_router = APIRouter(prefix="/conversations", tags=["对话总结模块"])


class CreateSessionRequest(BaseModel):
    user_id: str  # 前端传递的用户ID


class CreateSessionResponse(BaseModel):
    conversation_id: str  # 生成的会话ID（UUID）
    message: str = "会话创建成功"


# 创建会话接口（生成唯一ID）
@conversation_router.post("/createConversation", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest):
    conversation_id = ConversationService.create_conversation_id()
    return CreateSessionResponse(conversation_id=conversation_id)


# WebSocket对话接口
@conversation_router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        conversation_id: str,
        user_id: str,
        db: Session = Depends(get_db)  # 通过Depends注入db会话
):
    service = ConversationService()
    await service.handle_conversation_flow(websocket, conversation_id, user_id, db)

# 将路由添加到独立应用,测试用
app.include_router(conversation_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 