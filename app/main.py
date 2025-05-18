import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.userRouters import userRouter
from app.routers import hrafile_router
from app.routers import rag_chat
from app.routers import rag_knowledge
from app.routers.conversation_router import conversation_router
from app.utils.Interceptors import RequestInterceptor
from app.routers import hra_interpret_router

app = FastAPI()
app.include_router(userRouter, prefix="/user", tags=["用户功能模块"])
app.include_router(conversation_router)
app.include_router(hrafile_router.router,tags=["HRA报告上传存储"])
app.include_router(rag_chat.router,tags=["rag对话"])
app.include_router(rag_knowledge.router,tags=["rag知识库管理模块"])
app.include_router(hra_interpret_router.router)

app.add_middleware(RequestInterceptor)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
@app.get("/home")
async def home():
    return {"message": "hello world~"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080)
