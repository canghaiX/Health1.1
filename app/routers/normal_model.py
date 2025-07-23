
from typing import Optional, Dict,List
import json
from datetime import datetime,timezone
from app.config import get_logger

from app.database.utils import get_db  
from app.models.qadata import QaData  
from openai import AsyncOpenAI
import time
from fastapi import APIRouter, Body, HTTPException, Depends,FastAPI
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# 配置日志
logger = get_logger(__name__)

# 初始化OpenAI客户端
client = AsyncOpenAI(
    api_key='empty',
    base_url="http://localhost:8000/v1",
)

app = FastAPI()
router = APIRouter()
@router.post("/normal_model/",summary="普通问答模型接口")
async def generate_hra_summary(system_content:str,user_content:str) :
    try:
        response = await client.chat.completions.create(
                            model="/models/model",
                            messages = [
                                        {
                                            'role': 'system',
                                            'content': system_content
                                        },
                                        {
                                            'role': 'user',
                                            'content': user_content
                                        }
                                    ],
                            max_tokens=10240,
                            temperature=0.01,
                            top_p=0.1,
                            stream=False
                        )
        result = response.choices[0].message.content
        index = result.find('</think>')
        result= result[index+9:].lstrip() if index != -1 else result
        logger.info(f"普通问答问题提示词：{user_content}\n普通问答回复: {result}")
    except Exception as e:
        logger.error(f"普通问答处理失败: {e}")
        result = "处理失败"
        return {'code':500,
                'message':result
                }
    return {'code':200,
        'message':result
        }

# 将路由添加到独立应用,测试用
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7999) 