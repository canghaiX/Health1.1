# Health1.1（5.18 - 14.41）/app/routers/rag_chat_with_hra.py
"""
带有HRA数据处理的知识库问答接口
"""
from fastapi import APIRouter, Body, Request , FastAPI
from app.config import get_logger
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import json
from app.routers.rag_knowledge import retrieval
from openai import AsyncOpenAI
from app.utils.hra_json_filter import hra_json_filter
from app.utils.sql_helper import SQLHelper  # 导入 SQLHelper 类

# # 创建一个独立的 FastAPI 应用,用作测试
# app = FastAPI(title="HRA报告解读服务")


# qwen模型api，模型名称为qwen2.5-32b-instruct
client = AsyncOpenAI(
    api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

router = APIRouter(tags=["HRA报告解读"])

logger = get_logger(__name__)


@router.post("/knowledge_base_chat_with_hra/")
async def knowledge_base_chat_with_hra(
        user_id: int = Body(..., description='用户ID'),
        kbId: Optional[str] = Body(None, description='知识库编号，不给时默认从所有知识库里检索'),
        query: str = Body(..., description='用户输入', examples=["你是谁"]),
        history: list = Body([], description="历史对话记录"),
        stream: bool = Body(False, description="是否流式输出"),
        modelName: str = Body('qwen2.5-32b-instruct', description='模型名称'),
        temperature: float = Body(0.1, description="LLM 采样温度"),
        limit: int = Body(3, description="查询最相关的limit个结果")
):
    try:
        sql_helper = SQLHelper()  # 初始化 SQLHelper 类
        # 从数据库中获取该用户的最新hra_json_data
        query = "SELECT hra_json_data FROM hra_data WHERE user_id = %s ORDER BY id DESC LIMIT 1"
        result = sql_helper.fetch_one(query, (user_id,))

        if result is None:
            logger.info(f"未找到用户 {user_id} 的HRA数据")
            hra_result_str = ""
        else:
            hra_json_data = result['hra_json_data']
            logger.info(f"从数据库获取的 HRA JSON 数据: {hra_json_data}")
            try:
                # 尝试解析 HRA JSON 数据
                hra_json_data = json.loads(hra_json_data)
                hra_result_str = ""
                # 使用 hra_json_filter 函数处理 hra_json_data
                hra_result_str = hra_json_filter(hra_json_data)
            except json.JSONDecodeError as e:
                # 记录 JSON 解析错误信息
                logger.info(f"解析 HRA JSON 数据时出错: {e}")
                logger.info(f"待解析的 HRA JSON 数据: {hra_json_data}")
                # hra_result_str = ""
            
                # # 使用 hra_json_filter 函数处理 hra_json_data
                # hra_result_str = hra_json_filter(hra_json_data)
                # logger.info(f"这是给模型传递的hra报告信息{hra_result_str}")

        async def event_generator(query, history, stream, modelName, temperature, kbId, limit, hra_result_str):
            logger.info(f"{kbId}知识库编号")
            # 检索逻辑
            source = retrieval(kbId=kbId, query=query, limit=limit)
            # logger.info(source)

            result = []
            if not source:
                logger.info('检索结果为空')
            else:
                # logger.info(source['files'])
                result = source['files']
            
            logger.info(f"这是给模型传递的hra报告信息{hra_result_str}")

            input = f"请依据检索结果，对用户的HRA体检数据进行解读，给出医疗建议以及饮食运动建议，若检索结果无参考价值，忽略检索内容进行作答。检索结果: {result}\n用户HRA数据: {hra_result_str}\n"
            logger.info(f"问题: {input}")
            messages = [
                {
                    'role': 'system',
                    'content': '你现在的身份是惠斯安普公司开发的医疗助手大模型，能够根据病人情况给出诊疗建议。'
                },
                {
                    'role': 'user',
                    'content': f'{input}'
                },
            ]
            # 将history中的字典数据插入到messages列表的第二个位置
            messages[1:1] = history
            logger.info(f"完整的对话消息: {messages}")

            if stream:
                async for part in await client.chat.completions.create(
                        model=modelName,
                        messages=messages,
                        stream=True,
                        temperature=temperature,
                        max_tokens=4096,
                        stream_options={"include_usage": True}
                ):
                    logger.info(part)
                    if part.choices:
                        delta_content = part.choices[0].delta.content
                        logger.info(delta_content)
                        logger.info({"data": json.dumps({"answer": delta_content}, ensure_ascii=False)})
                        yield {"data": json.dumps({"answer": delta_content}, ensure_ascii=False)}

                yield {
                    "data": json.dumps({"files": source.get("files")}, ensure_ascii=False)
                }
            else:
                response = await client.chat.completions.create(
                    model=modelName,
                    messages=messages,
                    stream=False,
                    temperature=temperature
                )
                full_content = response.choices[0].message.content
                logger.info(full_content)
                yield {
                    "data": json.dumps(
                        {
                            "answer": full_content,
                            "files": source.get("files")
                        }, ensure_ascii=False)
                }

        return EventSourceResponse(event_generator(query, history, stream, modelName, temperature, kbId, limit,
                                                   hra_result_str))
    except Exception as e:
        logger.error(f"发生错误: {e}")
        return {"code": 500, "message": f"发生错误: {str(e)}"}
    
# # 将路由添加到独立应用,测试用
# app.include_router(router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000) 