from typing import List

from fastapi import APIRouter, Header, Body
from starlette.requests import Request
from app.services.conversationService import ConversationService

conversationRouter = APIRouter()


@conversationRouter.post("/singleQA")
async def singleQA(request: Request, question: str = Body(..., embed=True)):
    userId = request.headers.get("userId")
    return ConversationService.singleQA(question, userId)

@conversationRouter.post("/multiQA")
async def multiQA(request: Request):
    userId = request.headers.get("userId")
    return ConversationService.multiQA(userId)