#5.18 暂时没有跑通，跑通之后可以放到app文件夹下
from fastapi import APIRouter, WebSocket, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.conversationService import ConversationService
from app.models.conversation_model import get_db

conversation_router = APIRouter(prefix="/conversations", tags=["对话总结模块"])
service = ConversationService()

class CreateSessionRequest(BaseModel):
    user_id: str  # 前端传递的用户ID
    kb_id: str  # 前端传递要关联的知识库ID

class CreateSessionResponse(BaseModel):
    conversation_id: str  # 生成的会话ID（UUID）
    message: str = "会话创建成功"


# 创建会话接口（生成唯一ID）
@conversation_router.post("/createConversation", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest):
    conversation_id = ConversationService.create_conversation_id()
    service.bind_conversation_kb(conversation_id, request.kb_id)
    return CreateSessionResponse(conversation_id=conversation_id)


# WebSocket对话接口
@conversation_router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        conversation_id: str,
        user_id: str,
        db: Session = Depends(get_db)  # 通过Depends注入db会话
):
    kb_id = service.get_kb_by_id(conversation_id)  # 若值为‘’，则未关联知识库
    await service.handle_conversation_flow(websocket, conversation_id, user_id, db, kb_id)



from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI()

# 将 conversation_router 包含到应用中
app.include_router(conversation_router)

if __name__ == "__main__":
    import uvicorn
    # 运行 FastAPI 应用
    uvicorn.run(app, host="0.0.0.0", port=8000)
