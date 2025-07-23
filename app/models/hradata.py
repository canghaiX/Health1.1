from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Text
from app.database.base import Base


class HraData(Base):
    """HRA数据表模型"""
    __tablename__ = 'hra_data'
    
    user_id = Column(Integer,ForeignKey('users.user_id'),primary_key=True,nullable=False, comment='users表的id，作外键')
    hra_data = Column(Text, nullable=False, comment='最新一次的hra报告的json数据')
    hra_date = Column(DateTime, nullable=False, comment='最新一次的hra报告的json数据存入数据库的时间')