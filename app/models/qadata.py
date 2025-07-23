from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Text
from app.database.base import Base


class QaData(Base):
    """HRA报告解读及对话信息表"""
    __tablename__ = 'qa_data'

    user_id = Column(Integer, ForeignKey('users.user_id'),primary_key=True, comment='用户唯一标识')
    hra_qa_data = Column(Text, nullable=True, comment='由HRA报告解析产生的问答数据')
    qa_date = Column(DateTime, nullable=True, comment='记录最近一次HRA报告解析产生的问答数据存放的时间')
    hra_report_data = Column(Text, nullable=True, comment='由HRA报告对各个系统的解析以及用户问答的数据')
    report_date = Column(DateTime, nullable=True, comment='记录最近一次HRA报告解读存放时间')
    hra_report_summary = Column(Text, nullable=True, comment='HRA报告总结内容')