# apps/conversation_model.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config import settings  # 从配置文件获取数据库连接信息

# 初始化数据库引擎（使用config中的配置）
engine = create_engine(
    settings.database_url,
    echo=True  # 开发环境打印SQL日志（生产环境可关闭）
)

# 创建数据库会话工厂（自动管理事务）
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()  # 基类（用于模型继承）


class ConversationSummary(Base):
    """对话总结表（存储最终总结）"""
    __tablename__ = "conversations"

    uuid = Column(String(36), primary_key=True)  # 会话ID（conversation_id）
    summary = Column(String(4000), nullable=False)  # LLM生成的总结内容
    user_id = Column(String(50), nullable=False)  # 用户ID
    create_time = Column(DateTime, nullable=False)  # 总结生成时间


def get_db():
    """依赖函数：获取数据库会话（用于FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db  # 提供会话给请求使用
    finally:
        db.close()  # 请求结束后关闭会话
