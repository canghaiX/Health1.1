import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.userRouters import userRouter
from .routers import hrafile_router
from .routers import rag_chat
from .routers import rag_knowledge
from .routers.conversation_router import conversation_router
from .utils.Interceptors import RequestInterceptor

app = FastAPI()
app.include_router(userRouter, prefix="/user", tags=["用户功能模块"])
app.include_router(conversation_router)
app.include_router(hrafile_router.router)
app.include_router(rag_chat.router)
app.include_router(rag_knowledge.router)

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
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
