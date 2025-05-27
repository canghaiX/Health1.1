from fastapi import APIRouter, Body, Request, FastAPI, HTTPException, status
from app.config import get_logger
from sse_starlette.sse import EventSourceResponse
from typing import Optional
from pydantic import BaseModel
import json
from app.routers.rag_knowledge import retrieval
from openai import AsyncOpenAI
from app.utils.sql_helper import SQLHelper
from app.utils.radar_filter import HealthDataProcessor
from fastapi.responses import JSONResponse

# 单独测试用，创建FastAPI应用
app = FastAPI(title="雷达波数据分析")

# qwen模型api，模型名称为qwen2.5-32b-instruct
client = AsyncOpenAI(
    api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

router = APIRouter(tags=["雷达波数据分析"])

logger = get_logger(__name__)

# 请求体数据模型
class RadarData(BaseModel):
    success: str
    failReason: str
    data: dict

@router.post("/detect_radar_anomaly/")
async def detect_radar_anomaly(
    user_id: int = Body(..., description='用户ID'),
    kbId: Optional[str] = Body(None, description='知识库编号，不给时默认从所有知识库里检索'),
    data: RadarData = Body(...),
    history: list = Body([], description="历史对话记录"),
    stream: bool = Body(False, description="是否流式输出"),
    modelName: str = Body('qwen2.5-32b-instruct', description='模型名称'),
    temperature: float = Body(0.1, description="LLM采样温度"),
    limit: int = Body(3, description="查询最相关的limit个结果")
):
    try:
        # 将请求体转换为JSON格式
        json_data = data.model_dump()
        
        # 实例化
        processor = HealthDataProcessor(json_data)
        
        # 验证数据格式和状态
        process_result = processor.process()
        if process_result in [processor.error_messages["invalid_format"], processor.error_messages["invalid_status"]]:
            raise HTTPException(status_code=400, detail="数据格式或状态异常")
        
        is_normal = processor.is_health_data_normal()  
        if not is_normal:
            # 雷达波数据出现异常，准备RAG问答
            prompt_anomalies = processor.process()
            anomalies = processor.get_anomalies()
            
            
            # 构建异常提示词
            anomaly_prompt = f"用户的雷达波健康检测数据出现异常。异常详情：{prompt_anomalies}。请结合这些异常情况，给出相应的医疗建议、饮食和运动建议。"
            
            async def event_generator():
                # 检索逻辑
                source = retrieval(kbId=kbId, query=anomaly_prompt, limit=limit)
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
                # 将history中的字典数据插入到messages列表的第二个位置
                messages[1:1] = history
                logger.info(f"完整的对话消息: {messages}")

                if stream:
                    async for part in await client.chat.completions.create(
                            model=modelName,
                            messages=messages,
                            stream=True,
                            temperature=temperature,
                            max_tokens=4096,
                            stream_options={"include_usage": True}
                    ):
                        if part.choices:
                            delta_content = part.choices[0].delta.content
                            yield {"data": json.dumps({"answer": delta_content}, ensure_ascii=False)}

                    yield {
                        "data": json.dumps({"files": source.get("files")}, ensure_ascii=False)
                    }
                else:
                    response = await client.chat.completions.create(
                        model=modelName,
                        messages=messages,
                        stream=False,
                        temperature=temperature
                    )
                    full_content = response.choices[0].message.content
                    yield {
                        "data": json.dumps(
                            {
                                "answer": full_content,
                                "anomalies": anomalies
                            }, ensure_ascii=False)
                    }

            return EventSourceResponse(event_generator())
        else:
            # 无异常时返回204状态码
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    
    except Exception as e:
        logger.error(f"发生错误: {e}")
        return {"code": 500, "message": f"发生错误: {str(e)}"}

#单独测试用，添加路由到应用
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)