import requests
import re
import json

# 启动本地服务时的地址
url = 'http://localhost:11434/v1/chat/completions'

# 用户输入的消息
messages = [
    {'role': 'user', 'content': '1加1等于几？'}
]

# 请求体
data = {
    "model": "deepseek-r1:32b",  # 模型ID
    "messages": messages,
    "stream": True  # 启用流式输出
}
# print(f"即将发送请求到ollama模型服务")
# 发送请求到ollama模型服务
response = requests.post(url, json=data, stream=True)
# print(f"发送成功")
# 检查请求是否成功
if response.status_code == 200:
    done_reasoning = False

    # 实时处理流式输出
    for chunk in response.iter_lines():
        if chunk:
            # 移除 "data: " 前缀
            chunk_str = chunk.decode('utf-8').lstrip('data: ').strip()

            # 只有在去掉前缀后还有数据时才尝试解析 JSON
            if chunk_str:
                try:
                    chunk_data = json.loads(chunk_str)
                    # print(chunk_data)  # 打印解析后的数据
                except json.JSONDecodeError as e:
                    # print(f"Failed to decode JSON: {e}")
                    continue  # 如果解析失败，跳过该 chunk
            else:
                print("Received empty chunk")

            # 获取reasoning_content和content
            delta = chunk_data.get("choices", [{}])[0].get("delta", {})
            reasoning_chunk = delta.get("reasoning_content", "")
            answer_chunk = delta.get("content", "")

            # 只打印最终答案，不显示思考过程
            if answer_chunk:
                if not done_reasoning:
                    # print('\n\n === Final Answer ===\n')
                    done_reasoning = True
                # 清理思考过程 <think> 标签及其内容
                answer_chunk = re.sub(r'<think>.*?</think>', '', answer_chunk)
                answer_chunk = re.sub(r'<think>|</think>', '', answer_chunk)
                print(answer_chunk, end='', flush=True)

else:
    print(f"Request failed with status code {response.status_code}")

print()