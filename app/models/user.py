from sqlalchemy import Column, Integer, String
from app.database.base import Base

class User(Base):
    """用户表模型"""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, comment='用户唯一标识')
    user_name = Column(String(80), nullable=False, comment='用户姓名')
    phone = Column(String(11), nullable=False, comment='手机号')
    ex_field = Column(String(255), nullable=True, comment='拓展字段')
