from openai import OpenAI
import os

# 初始化OpenAI客户端
client = OpenAI(
    api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

messages = [{"role": "user", "content": "今天几月几号"}]

completion = client.chat.completions.create(
    model="qwen2.5-32b-instruct",  # 您可以按需更换为其它深度思考模型
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "今天几月几号？"},
    ],
)

print(completion.choices[0].message.content)

