# app/routers/file_router.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.hrafile_service import save_uploaded_file
from app.database import get_db

router = APIRouter(
    prefix="/files",
    tags=["文件上传"],
)

@router.post("/upload/pdf", response_model=dict)
async def upload_pdf_file(
    file: UploadFile = File(...,max_size=50 * 1024 * 1024),  #限制文件上传大小为50MB
    db: Session = Depends(get_db)
):
    # 验证文件类型
    if not file.content_type.startswith("application/pdf"):
        raise HTTPException(status_code=400, detail="请上传PDF格式文件")
    
    # 保存文件
    db_file = save_uploaded_file(file, db)
    
    return {
        "message": "上传成功",
        "file_id": db_file.id,
        "file_name": db_file.file_name,
        "upload_time": db_file.upload_time
    }