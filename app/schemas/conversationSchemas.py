from pydantic import BaseModel


# 目前用不到
class ConversationIn(BaseModel):
    UUID: str
    String: str
    userId: str
