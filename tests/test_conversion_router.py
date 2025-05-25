#用于测试conversion_router.py中的socket方法
import asyncio
import json
import websockets

async def connect_to_websocket(conversation_id, user_id):
    uri = f"ws://localhost:8000/conversations/ws/{conversation_id}?user_id={user_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            # 持续对话
            while True:
                user_input = input("请输入问题（输入q退出）: ")
                if user_input.lower() == 'q':
                    break
                
                # 发送JSON格式消息
                message = {"query": user_input}
                await websocket.send(json.dumps(message))
                
                # 接收响应
                response = await websocket.recv()
                print(f"AI回复: {response}")
    
    except websockets.exceptions.ConnectionClosedOK:
        print("连接已正常关闭")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"连接意外关闭: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
        

if __name__ == "__main__":
    # 先调用 createConversation 接口获取 conversation_id
    # 这里假设你已经有了 conversation_id 和 user_id
    conversation_id = "8d649278-297a-4dfa-a1ab-856d8d497772"
    user_id = "1"
    asyncio.run(connect_to_websocket(conversation_id, user_id))