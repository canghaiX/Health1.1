import json
from urllib import request

from fastapi import APIRouter
from app.schemas.userSchemas import UserIn, UserOut
from app.services.dealWithJson import json_test
from app.services.userServices import UserService

userRouter = APIRouter()

@userRouter.get("/getUserList")
async def getUserList():
    return {"users": [{}]}

#处理json
@userRouter.post("/loginIn",methods=["POST"])
async def loginIn():
    data=request.get_json(force=True)
    data1=json.loads(data)
    json_test(data1)
    return {"message": ""}


@userRouter.post("/register")
async def registerUser(user: UserIn):
    userInfo = UserService.addUser(user)
    userOut = UserOut(id=userInfo.id, username=userInfo.username, email=userInfo.email)
    return {"message": userOut}
