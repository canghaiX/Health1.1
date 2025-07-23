import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.userRouters import userRouter
from app.routers import hrafile_router
from app.routers import rag_chat
from app.routers import rag_knowledge
from app.routers.conversation_router import conversation_router
from app.utils.Interceptors import RequestInterceptor
#from app.routers import hra_interpret_router2_new                        #测试时暂时修改为2_new
#from app.routers import radar_receive
#from app.routers import radar_continuetalk_new                           #测试时暂时修改为_new
from app.models.hrafile_model import UploadedFile
from app.routers import radarwave_livetalking
from app.routers import normal_model_qa
from app.routers import hra_report_fixed
from app.routers import normal_model
from app.routers import hra_report_store
from app.routers import hra_qadata_store


app = FastAPI()
app.include_router(userRouter, prefix="/user", tags=["用户功能模块"])
app.include_router(conversation_router)
app.include_router(hrafile_router.router,tags=["HRA报告上传存储"])
app.include_router(rag_chat.router,tags=["rag对话"])
app.include_router(rag_knowledge.router,tags=["rag知识库管理模块"])
#app.include_router(hra_interpret_router2_new.router)                      #测试时暂时修改为2_new
#app.include_router(radar_receive.router)
#app.include_router(radar_continuetalk_new.conversation_router)            #测试时暂时修改为_new
app.include_router(radarwave_livetalking.router,tags=["6.19雷达波接口"]) 
app.include_router(normal_model_qa.router,tags=["6.21问答总结和普通模型对话接口"])          
app.include_router(hra_report_fixed.router,prefix="/v1",tags=["6.24hra分系统解析、问答"])
app.include_router(normal_model.router,tags=["7.3可传模型提示词，普通模型问答接口"])
app.include_router(hra_report_store.router)
app.include_router(hra_qadata_store.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(RequestInterceptor)

@app.get("/home")
async def home():
    return {"message": "hello world~"}


if __name__ == "__main__":
    uvicorn.run("app.main:app",host="0.0.0.0", port=8100)





#          python -m app.main >log/hsap.log 2>&1          输出日志
