from fastapi import APIRouter, Body, WebSocket, HTTPException, status,Depends,Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.conversationService import ConversationService
from app.database.utils import get_db
from uuid import uuid4
import json
import asyncio
from typing import Dict, Optional
from fastapi.responses import JSONResponse
from app.config import get_logger
from app.utils.radar_filter import HealthDataProcessor
from app.routers.rag_knowledge import retrieval
from openai import AsyncOpenAI

conversation_router = APIRouter(prefix="/conversations", tags=["雷达波监测以及主动问答"])
service = ConversationService()

# 存储活跃的WebSocket连接
active_connections: Dict[str, WebSocket] = {}
# 存储会话信息
sessions: Dict[str, dict] = {}

client = AsyncOpenAI(
    api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# 雷达波数据模型
class RadarData(BaseModel):
    success: str
    failReason: str
    data: dict

logger = get_logger(__name__)

# 处理雷达波数据并自动建立会话
@conversation_router.post("/processRadarData")
async def process_radar_data(
    user_id: str = Body(..., embed=True),
    kb_id: str = Body(..., embed=True),
    data: RadarData = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    try:
        json_data = data.model_dump()
        #json_data = data
        processor = HealthDataProcessor(json_data)
        # 验证数据格式和状态
        process_result = processor.process()
        if process_result in [processor.error_messages["invalid_format"], processor.error_messages["invalid_status"]]:
            raise HTTPException(status_code=400, detail="数据格式或状态异常")
        
        is_anomaly = processor.is_health_data_normal()  
        
        if is_anomaly:
            # 无异常时返回204状态码
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        
        prompt_anomalies = processor.process()
        # #获取具体异常信息，暂时用不到
        # anomalies = processor.get_anomalies()
        # 构建异常提示词
        anomaly_prompt = f"用户的雷达波健康检测数据出现异常。异常详情：{prompt_anomalies}。请结合这些异常情况，给出相应的医疗建议、饮食和运动建议。"
        
        
        # 检索逻辑
        source = retrieval(kbId=kb_id, query=anomaly_prompt, limit=1)
        result = source['files'] if source else []
        
        input = f"请依据检索结果，对用户的健康数据异常进行解读，进行相应的健康情况问询。用户异常数据: {anomaly_prompt}\n检索结果: {result}"
        logger.info(f"问题: {input}")
        
        messages = [
            {
                'role': 'system',
                'content': '你现在的身份是惠斯安普公司开发的医疗助手大模型，能够根据病人情况给出身体健康建议。给出的建议要是口语化文本，能直接读出来，不要带有逗号句号以外的标点符号，不要用markdown标记'
            },
            {
                'role': 'user',
                'content': f'{input}'
            },
        ]
        logger.info(f"完整的对话消息: {messages}")
        #暂时不考虑流式
        # if stream:
        #     async for part in await client.chat.completions.create(
        #             model='qwen2.5-32b-instruct',
        #             messages=messages,
        #             stream=True,
        #             temperature=0.1,
        #             max_tokens=4096,
        #             stream_options={"include_usage": True}
        #     ):
        #         if part.choices:
        #             delta_content = part.choices[0].delta.content
        #             yield {"data": json.dumps({"answer": delta_content}, ensure_ascii=False)}

        #     yield {
        #         "data": json.dumps({"files": source.get("files")}, ensure_ascii=False)
        #     }
        # else:
        response = await client.chat.completions.create(
            model='qwen2.5-32b-instruct',
            messages=messages,
            stream=False,
            temperature=0.1
        )
        rag_response = response.choices[0].message.content
       
        
        # 生成唯一的conversation_id
        conversation_id = str(uuid4())
        
        service.bind_conversation_kb(conversation_id, kb_id)
        # 存储会话信息
        sessions[conversation_id] = {
            "user_id": user_id,
            "kb_id": kb_id,
            "rag_response": rag_response,
            "created_at": asyncio.get_event_loop().time(),

            
            #添加初始状态
            "state":"awaiting_user_response",
            "inquiry_question":"您有哪些不适症状？请描述一下。"
        }
        
        # 返回包含conversation_id和WebSocket URL的响应
        return {
            "status": "anomaly_detected",
            "conversation_id": conversation_id,
            "initial_response": rag_response,
            "websocket_url": f"ws://localhost:8010/conversations/ws/{conversation_id}",
            "message": "检测到异常，已生成会话，请建立WebSocket连接继续对话"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # 修改后的WebSocket处理
# @conversation_router.websocket("/ws/{conversation_id}")      #"/ws/{conversation_id}"
# async def websocket_endpoint(
#         websocket: WebSocket,
#         conversation_id: str,
#         user_id: str,
#         db: Session = Depends(get_db),
# ):
    


#     if conversation_id not in sessions:
#         await websocket.close(code=1008, reason="无效的会话ID")
#         return

#     try:
#         await websocket.accept()
#         session = sessions[conversation_id]
#         active_connections[conversation_id] = websocket

#         # 第一阶段：发送询问问题
#         if session["state"] == "awaiting_user_response":
#             await websocket.send_json({
#                 "type": "question",
#                 "content": session["inquiry_question"]
#             })

#             # 等待用户回复
#             user_response = await websocket.receive_text()
#             session["user_response"] = user_response
#             session["state"] = "processing_response"

#         # 第二阶段：处理用户回复并生成建议
#         if session["state"] == "processing_response":
#             # 结合异常数据和用户回答进行RAG检索
#             combined_prompt = f"""
#             用户健康数据异常：{session["anomalies"]}
#             用户回答：{session["user_response"]}
#             请结合这些信息，给出专业的医疗建议、饮食和运动建议。
#             """

#             source = retrieval(kbId=session["kb_id"], query=combined_prompt, limit=1)
#             result = source['files'] if source else []

#             final_input = f"""
#             用户健康异常数据: {session["anomalies"]}
#             用户自述症状: {session["user_response"]}
#             请根据以上信息和以下检索结果，给出综合建议：
#             检索结果: {result}
#             """

#             final_messages = [
#                 {
#                     'role': 'system',
#                     'content': '你是医疗助手，需要根据健康数据和用户描述给出综合建议'
#                 },
#                 {
#                     'role': 'user',
#                     'content': final_input
#                 }
#             ]

#             final_response = await client.chat.completions.create(
#                 model='qwen2.5-32b-instruct',
#                 messages=final_messages,
#                 stream=False,
#                 temperature=0.1
#             )

#             final_advice = final_response.choices[0].message.content

#             await websocket.send_json({
#                 "type": "final_advice",
#                 "content": final_advice
#             })

#             # 保存完整对话记录
#             service.save_conversation(
#                 conversation_id,
#                 user_id,
#                 session["inquiry_question"],
#                 session["user_response"],
#                 final_advice,
#                 db
#             )

#     except Exception as e:
#         try:
#             await websocket.send_json({"type": "error", "message": str(e)})
#         except:
#             pass
#     finally:
#         if conversation_id in active_connections:
#             del active_connections[conversation_id]
#         if conversation_id in sessions:
#             del sessions[conversation_id]







# WebSocket对话接口
@conversation_router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    user_id: str,
    db: Session = Depends(get_db),
):
    # 检查会话是否存在
    print("已经进入websocket连接")
    if conversation_id not in sessions:
        await websocket.close(code=1008, reason="无效的会话ID")
        return
    
    try:
        # 接受WebSocket连接
        await websocket.accept()
        
        # 获取会话信息
        session = sessions[conversation_id]
        
        # # 发送初始RAG响应
        # await websocket.send_json({
        #     "type": "initial_response",
        #     "content": session["rag_response"]
        # })
        
        # 添加到活跃连接
        active_connections[conversation_id] = websocket
        
        # 调用服务处理对话流程
        await service.handle_conversation_flow(
            websocket, 
            conversation_id, 
            session["user_id"], 
            db, 
            session["kb_id"]
        )
    
    except Exception as e:
        # 错误处理
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close(code=1011, reason="处理过程中发生错误")
        except:
            pass
    finally:
        # 清理资源
        if conversation_id in active_connections:
            del active_connections[conversation_id]
        if conversation_id in sessions:
            del sessions[conversation_id]




# 创建FastAPI应用实例
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(conversation_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)