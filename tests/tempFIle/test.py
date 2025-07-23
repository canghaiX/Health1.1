# from openai import OpenAI,AsyncOpenAI
# import re

# #创建 OpenAI 兼容客户端（用于 ModelScope 的 DeepSeek 模型）
# client = OpenAI(
#     base_url='http://localhost:11434/v1',
#     api_key='ollama'  # 本地服务通常不需要api_key，留空
# )
# print(f"OpenAI创建成功")


# # response = client.chat.completions.create(
# #   model="deepseek-r1:32b",
# #   messages=[
# #     {"role": "system", "content": "You are a helpful assistant."},
# #     {"role": "user", "content": "Who won the world series in 2020?"},
# #     {"role": "assistant", "content": "The LA Dodgers won in 2020."},
# #     {"role": "user", "content": "Where was it played?"}
# #   ]
# # )
# # 调用 DeepSeek 模型生成对话回复
# response = client.chat.completions.create(
#     model='deepseek-r1:32b',
#     # model='deepseek-chat',
#     messages=[
#         {
#             'role': 'user',
#             'content': '帮我写一段代码'
#         },
#         {
#             'role': 'user',
#             'content': 'HELLO'
#         }
#     ],
#         response_format={
#         'type': 'json_object'
#     },
#     stream=False  # 启用流式输出
# )
# print(f"连接成功")
# full_content = response.choices[0].message.content
# print(full_content)
# # full_content = re.sub(r'<think>.*?</think>', '', full_content)
# # full_content = re.sub(r'<think>|</think>', '', full_content)
# # print(full_content)

from openai import OpenAI

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

response = client.chat.completions.create(
  model="deepseek-r1:32b",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The LA Dodgers won in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)
print(response.choices[0].message.content)