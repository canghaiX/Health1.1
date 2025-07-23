from sqlalchemy import create_engine,Column, Integer, String, Text, DateTime,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from app.database.session import AsyncSessionLocal
 



DATABASE_URL = "mysql+pymysql://hsap:yanshandaxue@localhost:3306/hsap"
engine = create_engine(
    DATABASE_URL,
    pool_size=20,       # 常规连接数
    max_overflow=10,    # 突发额外连接
    pool_pre_ping=True, # 自动检测失效连接
    pool_recycle=3600   # 1小时回收连接（防MySQL 8小时断开）
)

AsyncSessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()



class User(Base):
    """用户表模型"""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, comment='用户唯一标识')
    user_name = Column(String(80), nullable=False, comment='用户姓名')
    phone = Column(String(11), nullable=False, comment='手机号')
    ex_field = Column(String(255), nullable=True, comment='拓展字段')

    # 定义关系
    


class HraData(Base):
    """HRA数据表模型"""
    __tablename__ = 'hra_data'
    
    user_id = Column(Integer,ForeignKey('users.user_id'),primary_key=True,nullable=False, comment='users表的id，作外键')
    hra_data = Column(Text, nullable=False, comment='最新一次的hra报告的json数据')
    hra_date = Column(DateTime, nullable=False, comment='最新一次的hra报告的json数据存入数据库的时间')
    

    # 定义关系
    



class QaData(Base):
    """HRA报告解读及对话信息表"""
    __tablename__ = 'qa_data'

    user_id = Column(Integer, ForeignKey('users.user_id'),primary_key=True, comment='用户唯一标识')
    hra_qa_data = Column(Text, nullable=False, comment='由HRA报告解析产生的问答数据')
    qa_date = Column(DateTime, nullable=False, comment='记录最近一次HRA报告解析产生的问答数据存放的时间')
    hra_report_data = Column(Text, nullable=False, comment='由HRA报告解析及用户问答产生的报告')
    report_data = Column(DateTime, nullable=False, comment='记录最近一次HRA报告解读存放时间')

    # 定义关系
    



class RadarWave(Base):
    """雷达波数据表模型"""
    __tablename__ = 'radar_wave'

    user_id = Column(Integer,ForeignKey('users.user_id'), primary_key=True,nullable=False,comment='用户唯一标识，与HRA报告数据表相关联')
    radar_data = Column(Text,comment='最近一次无异常的雷达波数据')
    radar_date = Column(DateTime,comment='最近一次无异常的雷达波数据存放时间')
    abnormal_data = Column(DateTime,comment='最近一次触发异常的雷达波数据')
    abnormal_date = Column(DateTime,comment='最近一次触发异常的雷达波数据存放时间')
    equipment_id = Column(Integer, nullable=True, comment='设备id')
    
    # 定义关系
    




class ConversationSummary(Base):
    """对话总结表模型"""
    __tablename__ = 'conversations'

    uuid = Column(String(36), primary_key=True, comment='会话ID')
    summary = Column(String(4000), nullable=False, comment='LLM生成的总结内容')
    user_id = Column(String(50), ForeignKey('users.user_id'),nullable=False, comment='用户ID')
    create_time = Column(DateTime, nullable=False, comment='总结生成时间')




def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
