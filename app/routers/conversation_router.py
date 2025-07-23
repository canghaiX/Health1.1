from fastapi import APIRouter, WebSocket, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.conversationService import ConversationService
from app.database.utils import get_db

conversation_router = APIRouter(prefix="/conversations", tags=["对话总结模块"])
service = ConversationService()


class CreateSessionRequest(BaseModel):
    user_id: str  # 前端传递的用户ID
    kb_id: str  # 前端传递要关联的知识库ID


class CreateSessionResponse(BaseModel):
    conversation_id: str  # 生成的会话ID（UUID）
    message: str = "会话创建成功"


class MessageRequest(BaseModel):
    message: str


# 创建会话接口（生成唯一ID）
@conversation_router.post("/createConversation", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest):
    print("id")
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


@conversation_router.post("/api/np_get_res")
async def np_get_res(req: MessageRequest):
    res = await service.talk_api_numberPeople(req.message)
    print(req.message)
    print(res)
    if res:
        return {
            'status': 200,
            'response': res
        }
    return {
        'status': 500,
        'response': f'调用失败'
    }


from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI()

if __name__ == "__main__":
    import uvicorn

    # 运行 FastAPI 应用
    uvicorn.run(app, host="0.0.0.0", port=8010)
