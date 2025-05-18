#用于测试conversion_router.py中的socket方法
import asyncio
import websockets

async def connect_to_websocket(conversation_id, user_id):
    uri = f"ws://localhost:8000/conversations/ws/{conversation_id}?user_id={user_id}"
    async with websockets.connect(uri) as websocket:
        # 发送消息到服务器
        message = {"query": "你是谁"}
        await websocket.send(str(message))

        # 接收服务器的响应
        response = await websocket.recv()
        print(f"接收到服务器响应: {response}")

if __name__ == "__main__":
    # 先调用 createConversation 接口获取 conversation_id
    # 这里假设你已经有了 conversation_id 和 user_id
    conversation_id = "ed632b16-1fb0-4d21-aad2-108f23986b6f"
    user_id = "1"
    asyncio.run(connect_to_websocket(conversation_id, user_id))