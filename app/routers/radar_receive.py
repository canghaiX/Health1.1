from fastapi import FastAPI, HTTPException, Body ,status
from pydantic import BaseModel
import json
from app.utils.radar_filter import HealthDataProcessor  
from fastapi.responses import JSONResponse

app = FastAPI()

# 请求体数据模型（可选，根据实际数据结构调整）
class RadarData(BaseModel):
    success: str
    failReason: str
    data: dict  # 嵌套的 data 字段，对应示例数据结构

@app.post("/detect_radar_anomaly/")
async def detect_radar_anomaly(data: RadarData = Body(...)):
    try:
        # 将请求体转换为 JSON 格式
        json_data = data.model_dump()
        
        # 实例化
        processor = HealthDataProcessor(json_data)
        
        # 验证数据格式和状态（调用原有逻辑）
        if processor.process() in [processor.error_messages["invalid_format"], processor.error_messages["invalid_status"]]:
            raise HTTPException(status_code=400, detail="数据格式或状态异常")
        
        is_normal = processor.is_health_data_normal(json_data)  
        if not is_normal:
            # 雷达波数据出现异常，提示用户并启动实时问答流程
            prompt_anomalies = processor.process()
            anomalies = processor.get_anomalies()
            return {
                "status": "anomaly_detected",
                "conclusions": processor.process(),  
                "anomalies": anomalies  
            }
        else:
            # 无异常时返回204状态码，无响应体
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{str(e)}")