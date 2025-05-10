from typing import List

from pydantic import BaseModel
from app.database import SessionLocal
from app.models.conversation import Conversation
from app.utils.uuid_generate import generate_uid

# temp 存历史消息
temp: List[dict] = []
db = SessionLocal()


class ConversationService(BaseModel):
    def singleQA(question: str, userId: str):
        global temp
        # 预处理
        params = {
            "question": question,
            "userId": userId
        }
        # 调用LLM
        response = "Single answer" + question
        res_data = {
            "response": response,
            "userId": userId
        }
        temp.append(res_data)
        print(temp[0])
        return response

    def multiQA(userId: str):
        global temp
        # 所有回答进行总结
        params: List = []
        for t in temp:
            if t.get("userId") == userId:
                params.append(t.get("response"))

        # 调用LLM

        # 获取返回结果
        response = "Summary answer :"
        for param in params:
            response += param
        print(response)
        # 持久化
        UUID = generate_uid()
        db_conversation = Conversation(UUID=UUID, Summary=response, userId=userId)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return response
