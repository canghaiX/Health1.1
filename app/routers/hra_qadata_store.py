from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional,Dict,Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.qadata import QaData
from app.models.user import User
from app.database.utils import get_db
import json

router = APIRouter( tags=["数字人后端存储问答信息"])


class QaDataRequest(BaseModel):
    user_id: int
    #qa_data: str  # JSON格式的字符串
    qa_data: Dict[str, Any]  # 改为直接接受字典对象


class QaDataResponse(BaseModel):
    code: int
    message: str


@router.post("/read_hra_data/", response_model=QaDataResponse, summary="存储HRA报告解读问答记录")
async def read_hra_data(
        request: QaDataRequest,
        db: AsyncSession = Depends(get_db)
):
    """
    存储HRA报告解读问答记录接口

    参数:
    - user_id: 用户唯一标识ID
    - qa_data: HRA报告问答数据(字典对象)

    返回:
    - code: 状态码
    - message: 状态描述
    """
    try:
        # 1. 验证用户是否存在
        user_result = await db.execute(select(User).where(User.user_id == request.user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 2. 验证qa_data是否为有效的JSON
        # try:
        #     qa_data_json = json.loads(request.qa_data)
        # except json.JSONDecodeError:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="qa_data必须是有效的JSON格式"
        #     )

        # 2. 将字典转换为JSON字符串存储
        qa_data_str = json.dumps(request.qa_data, ensure_ascii=False)

        # 3. 检查是否已存在该用户的记录
        qa_result = await db.execute(select(QaData).where(QaData.user_id == request.user_id))
        existing_qa = qa_result.scalars().first()

        current_time = datetime.now()

        if existing_qa:
            # 更新现有记录
            existing_qa.hra_qa_data = qa_data_str
            existing_qa.qa_date = current_time
        else:
            # 创建新记录
            new_qa = QaData(
                user_id=request.user_id,
                hra_qa_data= qa_data_str,
                qa_date=current_time,
                hra_report_data=None,
                report_date=None,
                hra_report_summary=None
            )
            db.add(new_qa)

        await db.commit()

        return QaDataResponse(
            code=200,
            message="数据存储成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )