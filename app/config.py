import os

# 项目根目录（health1.1所在目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 文件存储目录
HRA_FILEBASE_DIR = os.path.join(PROJECT_ROOT, "hra_filebase")

#qwen平台模型调用api_key以及url
api_key='sk-7548be9550ca4f15a8b211deddbfc9e3'
base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"