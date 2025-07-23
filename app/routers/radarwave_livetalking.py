from fastapi import APIRouter, Depends, HTTPException, status,FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.database.utils import get_db

#from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # 新增select用于异步查询 

from datetime import datetime,timezone
import json
import logging
import re

app = FastAPI()
router = APIRouter()

# 请求体模型
class RadarData(BaseModel):
    user_id: int = Field(..., description="用户唯一标识ID")
    data: Dict[str, Any] = Field(..., description="雷达波数据对象")
# 响应体模型
class ProcessRadarDataResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field(..., description="状态描述")
    question: str = Field(..., description="健康问询问题")



async def detect_abnormalities(radar_data: dict) -> list:
    """检测雷达波数据中的异常"""
    abnormalities = []
    
    try:
        # 解析心脏数据
        heart_conclusion = radar_data.get('conclusion', {}).get('heartConclusion', '')
        breath_conclusion = radar_data.get('conclusion', {}).get('breathConclusion', '')
        
        if '疑似' in heart_conclusion :
            abnormalities.append(heart_conclusion)
        if '疑似' in breath_conclusion:
            abnormalities.append(breath_conclusion)

    
    except Exception as e:
        logging.error(f"异常检测错误: {str(e)}")
        raise
    
    return abnormalities

async def generate_health_question(abnormalities: list) -> str:
    """根据异常生成健康问询问题"""
    if not abnormalities:
        return ""
    
    # 根据异常类型生成不同问题
    questions = []
    
    #if "疑似早搏" in abnormalities:
    if "疑似早搏" in abnormalities or "心律不齐" in abnormalities:
        questions.append("您最近是否感到心慌或心跳不规律？")
    
    if "胸闷" in abnormalities or "胸痛" in abnormalities:
        questions.append("您是否有胸闷或气短的感觉？")
    
    
    if "呼吸不畅" in abnormalities or "呼吸深度异常" in abnormalities:
        questions.append("您是否有呼吸不畅或呼吸困难的情况？")
    
    
    # 合并问题
    if not questions:
        questions.append("您最近是否有不适的感觉？")
    
    return "检测到您的雷达波数据有异常，" + " ".join(questions)

async def save_radar_data( user_id: int, 
                    radar_data: dict, 
                    is_abnormal: bool, 
                    device_id: Optional[str] = None,
                    #db: Session = Depends(get_db)
                    db: AsyncSession = Depends(get_db)
                    ):
    
    """保存雷达波数据到数据库，符合radar_wave表结构"""
    try:
        # 导入模型（根据实际项目结构调整）
        from app.models.radarwave_model import RadarWave
        
        # 获取当前时间
        current_time =  datetime.now(timezone.utc)
        
        # 查询现有记录
        #record = db.query(RadarWave).filter(RadarWave.user_id == user_id).first()
        
        # 准备雷达波数据JSON
        radar_json = json.dumps(radar_data, ensure_ascii=False)

        # 异步查询现有记录
        stmt = select(RadarWave).where(RadarWave.user_id == user_id)
        result = await db.execute(stmt)
        record = result.scalars().first()
        
        if record:
            # 更新现有记录
            if is_abnormal:
                record.abnormal_data = radar_json
                record.abnormal_date = current_time
                if device_id:
                    record.device_id = device_id
            else:
                record.radar_data = radar_json
                record.radar_date = current_time
                if device_id:
                    record.device_id = device_id
        else:
            # 创建新记录
            if is_abnormal:
                new_record = RadarWave(
                    user_id=user_id,
                    abnormal_data=radar_json,
                    abnormal_date=current_time,
                    device_id=device_id
                )
            else:
                new_record = RadarWave(
                    user_id=user_id,
                    radar_data=radar_json,
                    radar_date=current_time,
                    device_id=device_id
                )
            await db.add(new_record)    #添加await
        
        await db.commit()   #添加await
        logging.info(f"雷达波数据已保存: 用户 {user_id}, 异常: {is_abnormal}")
    
    except Exception as e:
        await db.rollback()   # 添加await
        logging.error(f"保存雷达数据到数据库失败: {str(e)}")
        raise

@router.post("/processRadarData", 
            response_model=ProcessRadarDataResponse,
            responses={
                204: {"description": "数据正常，无异常"},    
                400: {"description": "请求参数错误"},
                500: {"description": "服务器内部错误"}
            })
async def process_radar_data(
    request: RadarData,
    #db: Session = Depends(get_db)
    db: AsyncSession = Depends(get_db)  # 改为AsyncSession
):
    """
    处理雷达波数据，检测异常并生成健康问询问题
    
    - **user_id**: 用户唯一标识ID
    - **data**: 雷达波数据对象
    - **device_id**: 采集设备ID (可选)
    """
    try:
        # 验证数据完整性
        if not request.data or 'data' not in request.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的雷达波数据格式"
            )
        
        radar_data = request.data.get('data', {})
        #logger.info(f"开始处理用户 {request.user_id} 的雷达波数据")
        
        # 检测异常
        abnormalities = await detect_abnormalities(radar_data)
        
        if not abnormalities:
            # 保存正常数据到数据库
            save_radar_data(
                user_id=request.user_id,
                radar_data=request.data,  # 保存整个请求数据
                is_abnormal=False,
                device_id = radar_data.get('data', {}).get('csgCollectId'),
                db=db
            )
            
            # 返回204状态码 - 无内容
            return {"code": 204, "message": "数据正常", "question": ""}
        
        # 生成健康问询问题
        question = await generate_health_question(abnormalities)
        
        # 保存异常数据到数据库
        save_radar_data(
            user_id=request.user_id,
            radar_data=request.data,  # 保存整个请求数据
            is_abnormal=True,
            #device_id = radar_data.get('data', {}).get('csgCollectId'),
            device_id=radar_data.get('csgCollectId'),
            db=db
        )
        
        return {
            "code": 200,
            "message": "检测到雷达波异常",
            "question": question
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"处理雷达数据错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )
    
# # 将路由添加到独立应用,测试用
# app.include_router(router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app,host="0.0.0.0", port=7999)