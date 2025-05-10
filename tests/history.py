from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory

# 配置Upstash Redis连接
URL = "<UPSTASH_REDIS_REST_URL>"
TOKEN = "<UPSTASH_REDIS_REST_TOKEN>"

# 创建消息历史记录对象，包含会话ID和消息时效性（TTL）
history = UpstashRedisChatMessageHistory(
    url=URL, token=TOKEN, ttl=10, session_id="my-test-session"
)

# 添加用户消息和AI回复
history.add_user_message("hello llm!")
history.add_ai_message("hello user!")

# 打印当前存储的消息列表
print(history.messages)
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory

# 配置Upstash Redis连接
URL = "<UPSTASH_REDIS_REST_URL>"
TOKEN = "<UPSTASH_REDIS_REST_TOKEN>"

# 创建消息历史记录对象，包含会话ID和消息时效性（TTL）
history = UpstashRedisChatMessageHistory(
    url=URL, token=TOKEN, ttl=10, session_id="my-test-session"
)

# 添加用户消息和AI回复
history.add_user_message("hello llm!")
history.add_ai_message("hello user!")

# 打印当前存储的消息列表
print(history.messages)
# UUID  key :value