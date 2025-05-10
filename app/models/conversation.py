from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversation'

    UUID = Column(String(20), primary_key=True, unique=True, index=True)
    Summary = Column(String(255))  # 总结性的评价
    userId = Column(String(20), unique=True, index=True)
