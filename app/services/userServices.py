from typing import List

from pydantic import BaseModel
from app.models.user import User

from app.database import SessionLocal
from app.schemas.userSchemas import UserOut, UserIn

db = SessionLocal()


class UserService(BaseModel):

    def getUserList(self):
        list = List[UserOut]
        list[0] = UserOut(id=1, usernmae="prk", email="123123@qq.com")
        return list

    def getUserById(id):
        return "通过ID查到了用户信息"

    def addUser(user: UserIn):
        db_user = User(username=user.username, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def isRepeatedByEmail(email):
        return ""
