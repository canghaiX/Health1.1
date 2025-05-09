from fastapi import APIRouter

from app.schemas.userSchemas import UserIn, UserOut
from app.services.userServices import UserService

userRouter = APIRouter()


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
