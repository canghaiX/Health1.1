from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 需要将拦截器添加到app中
class RequestInterceptor(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_userId = request.headers.get("userId")
        # 根据ID查对应的角色--权限
        '''
        roles = queryRolesById()
        urls=
        '''
        client_ip = request.client.host
        client_url = request.url.path
        print("拦截器||||||客户端IP：", client_ip,"访问地址：", client_url)
        response = await call_next(request)
        return response
