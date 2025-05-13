from fastapi import APIRouter
import json
from app.schemas.userSchemas import UserIn, UserOut
from app.services.userServices import UserService
import requests
userRouter = APIRouter()

#处理传过来的json
@userRouter.post("/user/dealWithJson",methods=["POST"])
async def dealWithJson():
    data=request.get_json(force=True)
    data1=json.loads(data)
    json_test()
    return {"message": ""}
@userRouter.get("/getUserList")
async def getUserList():
    return {"users": [{}]}


@userRouter.post("/loginIn")
async def loginIn(user: UserIn):
    return {"message": ""}


@userRouter.post("/register")
async def registerUser(user: UserIn):
    userInfo = UserService.addUser(user)
    userOut = UserOut(id=userInfo.id, username=userInfo.username, email=userInfo.email)
    return {"message": userOut}
