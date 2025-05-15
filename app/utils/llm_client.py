from openai import OpenAI
from app.config import settings
# 初始化OpenAI客户端（使用用户提供的配置）
client = OpenAI(
    base_url=settings.ARK_BASE_URL,
    api_key=settings.ARK_API_KEY  # 实际生产环境建议从环境变量获取
)

def get_llm_response(user_message: str) -> str:
    """调用方舟模型获取LLM回复"""
    try:
        response = client.chat.completions.create(
            model=settings.DOUBA_MODEL,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"LLM调用失败: {str(e)}")