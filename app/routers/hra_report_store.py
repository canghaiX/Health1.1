from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, insert
from datetime import datetime
import json
from typing import Optional

from app.models import HraData, User
from app.database.utils import get_db

router = APIRouter()


@router.post("/memory_hra_data/",
             response_class=JSONResponse,
             status_code=status.HTTP_201_CREATED,
             summary="存储用户HRA报告数据",
             tags=["HRA报告存储"])
async def store_hra_data(
        user_id: int,
        hra_data: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    """
    接收用户HRA报告数据，验证格式后存储到SQL数据库

    - **user_id**: 用户唯一标识ID
    - **hra_data**: HRA报告的JSON字符串
    """

    # 1. 参数验证
    if not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的用户ID，必须为正整数"
        )

    if not hra_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HRA数据不能为空"
        )

    # 2. 验证JSON格式
    try:
        json.loads(hra_data)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"HRA数据格式无效，请提供正确的JSON字符串. 错误详情: {str(e)}"
        )

    # 3. 检查用户是否存在
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户ID {user_id} 不存在"
        )

    # 4. 存储HRA数据（覆盖更新）
    current_time = datetime.now()
    try:
        # 检查是否已有记录
        existing_data = await db.get(HraData, user_id)

        if existing_data:
            # 更新现有记录
            stmt = (
                update(HraData)
                .where(HraData.user_id == user_id)
                .values(
                    hra_data=hra_data,
                    hra_date=current_time
                )
            )
        else:
            # 插入新记录
            stmt = insert(HraData).values(
                user_id=user_id,
                hra_data=hra_data,
                hra_date=current_time
            )

        await db.execute(stmt)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )

    # 5. 返回成功响应
    return {
        "code": status.HTTP_201_CREATED,
        "message": "HRA数据存储成功",
        "data": {
            "user_id": user_id,
            "store_time": current_time.isoformat()
        }
    }