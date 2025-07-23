from openai import OpenAI

#创建 OpenAI 兼容客户端（用于 ModelScope 的 DeepSeek 模型）
client = OpenAI(
    base_url='http://localhost:11434/v1/chat/completions',
    api_key=''  # 本地服务通常不需要api_key，留空
)
print(f"OpenAI创建成功")

# 调用 DeepSeek 模型生成对话回复
response = client.chat.completions.create(
    # model='deepseek-r1:32b',
    model='deepseek-chat',
    messages=[
        {
            'role': 'user',
            'content': '你好'
        }
    ],
        response_format={
        'type': 'json_object'
    },
    stream=True  # 启用流式输出
)
print(f"连接成功")
# 实时打印模型 reasoning 和最终回答
done_reasoning = False
for chunk in response:
    delta = chunk.choices[0].delta
    reasoning_chunk = getattr(delta, "reasoning_content", "")
    answer_chunk = getattr(delta, "content", "")
    
    if reasoning_chunk:
        print(reasoning_chunk, end='', flush=True)
    elif answer_chunk:
        if not done_reasoning:
            print('\n\n === Final Answer ===\n')
            done_reasoning = True
        print(answer_chunk, end='', flush=True)

# import re

# response = "<think>你好！</think>"
# cleaned_response = re.sub(r'<think>.*?</think>', '', response)
# print(cleaned_response)
