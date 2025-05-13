# app/services/file_service.py
import os
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.hrafile_model import UploadedFile
from config import HRA_FILEBASE_DIR

#文件存储路径
UPLOAD_DIR = HRA_FILEBASE_DIR  

def save_uploaded_file(file: UploadFile, db: Session, user_id: int = None):
    # 确保目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 生成唯一文件名（避免重名）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件到本地
    try:
        with open(file_path, "wb") as f:
            contents = file.file.read()
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    finally:
        file.file.close()
    
    # 保存文件信息到数据库
    db_file = UploadedFile(
        file_path=file_path,
        file_name=file.filename,
        user_id=user_id  # 关联用户
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file