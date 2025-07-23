# apps/conversation_model.py
from sqlalchemy import Column, String, DateTime
from app.database.base import Base


class ConversationSummary(Base):
    """对话总结表（存储最终总结）"""
    __tablename__ = "conversations"

    uuid = Column(String(36), primary_key=True)  # 会话ID（conversation_id）
    summary = Column(String(4000), nullable=False)  # LLM生成的总结内容
    user_id = Column(String(50), nullable=False)  # 用户ID
    create_time = Column(DateTime, nullable=False)  # 总结生成时间


