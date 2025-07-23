# Health1.1（5.18 - 14.41）/app/routers/rag_chat_with_hra.py
"""
带有HRA数据处理的知识库问答接口
"""
from fastapi import APIRouter, Body, Request, FastAPI, Query
from app.config import get_logger
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import json
from app.routers.rag_knowledge import retrieval
from openai import AsyncOpenAI
from app.utils.hra_json_filter import hra_json_filter
from app.utils.hra_json_filter import get_abnormal_data
from app.utils.hra_json_filter import get_question
from app.database.utils import get_db
from app.models.hradata import HraData
# from app.utils.sql_helper import SQLHelper  # 导入 SQLHelper 类
db = get_db()
# # 创建一个独立的 FastAPI 应用,用作测试
# app = FastAPI(title="HRA报告解读服务")


# qwen模型api，模型名称为qwen2.5-32b-instruct
client = AsyncOpenAI(
    api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

router = APIRouter(tags=["HRA报告解读"])

logger = get_logger(__name__)


# 公共逻辑函数（避免代码重复）
async def knowledge_base_chat_common(
        user_id: int,
        kbId: Optional[str],
        query: str,
        history: list,
        stream: bool,
        modelName: str,
        temperature: float,
        limit: int,
        que_ans: list
):
    print("======stream=====", stream)
    print(que_ans)
    # 如果还没有主动问答 生成主动问答
    if not que_ans:
        try:
            # sql_helper = SQLHelper()  # 初始化 SQLHelper 类
            # # 从数据库中获取该用户的最新hra_json_data
            # query = "SELECT hra_json_data FROM hra_data WHERE user_id = %s ORDER BY id DESC LIMIT 1"
            # result = sql_helper.fetch_one(query, (user_id,))
            result = db.query(HraData).filter(HraData.user_id == user_id)
            abnormal_data = ""
            if result is None:
                logger.info(f"未找到用户 {user_id} 的HRA数据")
            else:
                hra_json_data = result['hra_json_data']
                logger.info(f"从数据库获取的 HRA JSON 数据: {hra_json_data}")
                try:
                    # 尝试解析 HRA JSON 数据
                    hra_json_data = json.loads(hra_json_data)
                    hra_result_str = ""
                    # 使用 hra_json_filter 函数处理 hra_json_data
                    abnormal_data = get_abnormal_data(hra_json_data)
                except json.JSONDecodeError as e:
                    # 记录 JSON 解析错误信息
                    logger.info(f"解析 HRA JSON 数据时出错: {e}")
                    logger.info(f"待解析的 HRA JSON 数据: {hra_json_data}")
            if abnormal_data == "":
                # 无异常数据，无法生成主动问答
                return {
                    "status": 200,
                    "message": "无异常",
                    "data":{}
                }
            else:
                # 根据异常数据生成相关问答问题
                input = f"请围绕异常指标提出5个相关的问题，根据不同异常指标的严重情况，按优先级排序进行返回，回答要简短，只回答问题，不要有多余的字和符号。异常指标:{abnormal_data}"
                messages = [
                    {
                        'role': 'system',
                        'content': '你现在的身份是一名资深的问诊专家，请根据异常数据生成相关的问诊问题'
                    },
                    {
                        'role': 'user',
                        'content': input
                    },
                ]
                response = await client.chat.completions.create(
                    model=modelName,
                    messages=messages,
                    stream=False,
                    temperature=temperature
                )
                ques = response.choices[0].message.content

                logger.info(f"user_id:{user_id}")      #打印id
                #logger.info(f"  ques:,{ques}")

                print("ques:",ques)
                ###########################################
                question_list = get_question(abnormal_data)
                print("question_list:",question_list)
                return {
                    "status": 200,
                    "message": "您好，关于您的hra报告，我们检查到有异常数据，需要向您询问几个问题：",
                    "data": {
                        "que_ans": ques.split("\n")
                    }
                }

        except Exception as e:
            logger.error(f"发生错误: {e}")
            return {"code": 500, "message": f"发生错误: {str(e)}"}
    #que _ans格式
    que_anss = [
        "question:是否出现脖子增粗或甲状腺肿大？;answer:出现过",
        "question:是否被诊断过甲状腺功能亢进或减退？;answer:被诊断出亢进",
        "question:是否长期服用甲状腺素或降糖药物？;answer:没有长期服用，偶尔",
        "question:孕期是否出现妊娠糖尿病或甲状腺问题？;answer:没有",
        "question:是否监测过甲状腺功能（TSH、T3、T4）或性激素水平？;answer并没有"
    ]
    # 调用hra解析  分析que_ans
    try:
        # sql_helper = SQLHelper()  # 初始化 SQLHelper 类
        # # 从数据库中获取该用户的最新hra_json_data
        # query = "SELECT hra_json_data FROM hra_data WHERE user_id = %s ORDER BY id DESC LIMIT 1"
        # result = sql_helper.fetch_one(query, (user_id,))
        result = db.query(HraData).filter(HraData.user_id == user_id)
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

        async def event_generator():
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
            logger.info(f"这是给模型传递的问诊信息{que_ans}")

            # 验证历史对话格式
            valid_history = []
            for msg in history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    valid_history.append(msg)
                else:
                    logger.warning(f"跳过非法历史消息: {msg}")

            input = f"请依据检索结果和问诊信息，对用户的HRA体检数据进行解读，使用口语化文本解读，不要带除了冒号和逗号外的任何标点符号，给出医疗建议以及饮食运动建议，若检索结果无参考价值，忽略检索内容进行作答。检索结果: {result}\n问诊信息: {que_ans}\n用户HRA数据: {hra_result_str}\n"
            
            
            
            logger.info(f"问题: {input}")
            messages = [
                {
                    'role': 'system',
                    'content': '你现在的身份是惠斯安普公司开发的医疗助手大模型，能够根据病人情况给出诊疗建议。'
                },
                {
                    'role': 'user',
                    'content': input
                },
            ]
            # 将history中的字典数据插入到messages列表的第二个位置
            messages[1:1] = valid_history
            logger.info(f"完整的对话消息: {messages}")
            logger.info(f"发送给OpenAI的messages: {json.dumps(messages, ensure_ascii=False)}")

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
                    if part.choices and part.choices[0].delta.content:
                        logger.info(part.choices[0].delta.content)
                        yield {
                            "data": json.dumps({
                                "type": "answer_chunk",
                                "content": part.choices[0].delta.content
                            }, ensure_ascii=False)
                        }
                # 处理无检索结果的情况
                files = source.get("files", [])  # 确保files为列表
                yield {
                    "data": json.dumps({
                        "type": "final_files",
                        "content": files
                    }, ensure_ascii=False)
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

        return EventSourceResponse(event_generator())

    except Exception as e:
        logger.error(f"发生错误: {e}")
        return {"code": 500, "message": f"发生错误: {str(e)}"}


# 流式请求（GET）
@router.get("/knowledge_base_chat_with_hra/")
async def knowledge_base_chat_stream(
        user_id: int = Query(..., description='用户ID'),
        kbId: Optional[str] = Query(None, description='知识库编号'),
        query: str = Query(..., description='用户输入'),
        history: list = Query([], description="历史对话记录"),  # 自动解析查询参数中的JSON字符串
        stream: bool = Query(True, description="是否流式输出"),  # 默认开启流式
        modelName: str = Query('qwen2.5-32b-instruct', description='模型名称'),
        temperature: float = Query(0.1, description="LLM 采样温度"),
        limit: int = Query(3, description="查询最相关的limit个结果"),
        que_ans: list = Query([], description="主动问答")
):
    print(user_id, "  ", temperature, "  stream:", stream, "   history:", history)
    return await knowledge_base_chat_common(
        user_id, kbId, query, history, stream, modelName, temperature, limit, que_ans
    )


# 非流式请求（POST）
@router.post("/knowledge_base_chat_with_hra/")
async def knowledge_base_chat_non_stream(
        user_id: int = Body(..., description='用户ID'),
        kbId: Optional[str] = Body(None, description='知识库编号'),
        query: str = Body(..., description='用户输入'),
        history: list = Body([], description="历史对话记录"),
        stream: bool = Body(False, description="是否流式输出"),  # 默认关闭流式
        modelName: str = Body('qwen2.5-32b-instruct', description='模型名称'),
        temperature: float = Body(0.1, description="LLM 采样温度"),
        limit: int = Body(3, description="查询最相关的limit个结果"),
        que_ans: list = Body([], description="主动问答")
):
    return await knowledge_base_chat_common(
        user_id, kbId, query, history, stream, modelName, temperature, limit, que_ans
    )


@router.post("/knowledge_base_chat_with_hra1/")
async def knowledge_base_chat_with_hra1(
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
        # sql_helper = SQLHelper()  # 初始化 SQLHelper 类
        # # 从数据库中获取该用户的最新hra_json_data
        # query = "SELECT hra_json_data FROM hra_data WHERE user_id = %s ORDER BY id DESC LIMIT 1"
        # result = sql_helper.fetch_one(query, (user_id,))
        result = db.query(HraData).filter(HraData.user_id == user_id)
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
