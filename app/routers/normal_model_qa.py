from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict,List
import json
from datetime import datetime,timezone
from app.config import get_logger
from app.routers.rag_knowledge import retrieval
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


# 定义请求模型
class NormalModelQARequest(BaseModel):
    user_id: int = Field(..., description="用户唯一标识ID")
    kbId: Optional[str] = Field("2", description="知识库编号，未提供时默认从知识库2检索")
    total_interpret: bool = Field(..., description="是否进行HRA报告解析")
    query: Optional[str] = Field(None, description="用户输入的问题或指令")
    qa_data: List[Dict[str, str]] = Field(None, description="HRA报告解析的问答信息")
    

    @model_validator(mode="after")  # 模型验证完成后执行
    def validate_params(self):
        if self.total_interpret:
            if not self.qa_data:  # 直接访问已验证的qa_data
                raise ValueError("total_interpret为True时，qa_data不能为空")
        else:
            if not self.query:
                raise ValueError("total_interpret为False时，query不能为空")
        return self

# 定义响应模型
class NormalModelQAResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("", description="状态描述")
    answer: Optional[str] = Field(None, description="问答结果")
    summary: Optional[str] = Field(None, description="HRA报告总结内容")

# 初始化路由
router = APIRouter()

# HRA报告总结生成逻辑（示例，实际需根据业务逻辑实现）
async def generate_hra_summary(qa_data: List[Dict[str, str]],user_id:int,db:AsyncSession) -> str:
    """根据HRA问答数据生成总结报告（示例逻辑）"""
    result = []
    for item in qa_data:
        # 提取问题和答案
        question = item.get("question", "未知问题")
        answer = item.get("answer", "无答案")
        # 拼接成指定格式
        formatted_item = f"问题：{question} 答案：{answer}"
        result.append(formatted_item)
    result = "\n".join(result)
    interpret_data = await db.get(QaData, user_id)
    result += interpret_data.hra_report_data

    response = await client.chat.completions.create(
                    model="/models/model",
                    messages = [
                                {
                                    'role': 'system',
                                    'content': '你现在的身份是对话总结助手，能够根据文本进行总结。'
                                },
                                {
                                    'role': 'user',
                                    'content': f'这是需要总结的对话内容：{result},直接给出总结信息即可，不要有任何额外的话语,结果中的负号-请替换为汉字负。'
                                }
                            ],
                    max_tokens=10240,
                    temperature=0.01,
                    top_p=0.9,
                    stream=False
                )
    summary = response.choices[0].message.content
    index = summary.find('</think>')
    summary= summary[index+9:].lstrip() if index != -1 else summary
    qa_data = QaData(
            user_id=user_id,
            hra_report_summary=summary,
            report_date=datetime.now()
        )
    await db.merge(qa_data)
    await db.commit()
    print(summary)
    return summary

# 保存总结到数据库（示例，实际需根据数据库模型实现）
async def save_hra_summary_to_db( user_id: int, summary: str,db: AsyncSession) -> bool:
    """将HRA总结保存到数据库"""
    try: 
        current_time =  datetime.now(timezone.utc) 
        hra_data = QaData(
            user_id=user_id,
            hra_report_summary=summary,
            report_date=current_time
        )
        hra_data = await db.merge(hra_data)
        await db.commit()
        await db.refresh(hra_data)
        return True
    except Exception as e:
        logger.error(f"保存HRA总结失败: {str(e)}")
        await db.rollback()  
        return False

@router.post("/normal_model_qa/", response_model=NormalModelQAResponse)
async def normal_model_qa(
    request_data: NormalModelQARequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """基于RAG技术的普通模型问答接口"""
    try:
        if request_data.total_interpret:
            summary = await generate_hra_summary(request_data.qa_data,request_data.user_id,db)
            save_success = await save_hra_summary_to_db( request_data.user_id, summary,db)
            if not save_success:
                raise HTTPException(500, "数据库保存失败")
            return NormalModelQAResponse(
                code = 200,
                message="总结生成成功",
                answer ="",
                summary=summary
            )
        else:
            # source = retrieval(
            #     kbId=request_data.kbId,
            #     query=request_data.query,
            #     limit=3
            # )
            # context = "\n".join([f"[来源: {item.get('source')}]\n{item.get('content')}" 
            #                     for item in source.get("files", [])] or ["暂无相关信息"])
            
            prompt = f"用户问题: {request_data.query},回答要求：注意一定要口语化回答，不要带有逗号外任何标点符号"
            messages = [
                {"role": "system", "content": "你是惠斯安普公司开发的医疗助手,能给出一些医疗疗养建议"},
                {"role": "user", "content": prompt}
            ]
            
            response = await client.chat.completions.create(
                model="/models/model",
                messages=messages,
                temperature=0.01,
                max_tokens=20480
            )
            answer = response.choices[0].message.content.strip()
            index = answer.find('</think>')
            answer= answer[index+9:].lstrip() if index != -1 else answer
            answer= answer.replace('*',' ')
            return NormalModelQAResponse(
                code = 200,
                message="回答生成成功",
                answer=answer,
                summery = ""
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"接口异常: {str(e)}", exc_info=True)
        raise HTTPException(500, "服务器内部错误")
    

# 将路由添加到独立应用,测试用
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7999) 