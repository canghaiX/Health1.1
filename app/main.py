import uvicorn
from fastapi import FastAPI
from app.routers.userRouters import userRouter
from app.utils.Interceptors import RequestInterceptor

app = FastAPI()
app.include_router(userRouter, prefix="/user", tags=["用户功能模块"])
app.add_middleware(RequestInterceptor)

@app.get("/home")
async def home():
    return {"message": "hello world~"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
