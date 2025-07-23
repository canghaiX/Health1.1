from fastapi import APIRouter, Body, Request, FastAPI, Query, HTTPException
from app.config import get_logger
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import json
from app.routers.rag_knowledge import retrieval
from openai import AsyncOpenAI
from app.utils.hra_json_filter import hra_json_filter
from app.utils.hra_json_filter import get_abnormal_data
from app.utils.hra_json_filter import get_question
# from app.utils.sql_helper import SQLHelper  # 导入 SQLHelper 类
from app.database.utils import get_db
from app.models.hradata import HraData
db = get_db()

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
    if que_ans == ['[]']:
        print("que_ans is empty")
        que_ans = None
    else:
        print("que_ans:   ", que_ans)
    # 如果还没有主动问答 生成主动问答
    if not que_ans:
        try:
            # sql_helper = SQLHelper()  # 初始化 SQLHelper 类
            # 从数据库中获取该用户的最新hra_json_data
            # query = "SELECT hra_json_data FROM hra_data WHERE user_id = %s ORDER BY id DESC LIMIT 1"
            # result = sql_helper.fetch_one(query, (user_id,))
            result = db.query(HraData).filter(HraData.user_id == user_id)
            abnormal_data = ""
            if result is None:
                logger.info(f"未找到用户 {user_id} 的HRA数据")
                return {"code": 200, "message": f"未找到用户{user_id}的HRA数据！"}
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
        except Exception as e:
            logger.error(f"发生错误: {e}")
            return {"code": 500, "message": f"发生错误: {str(e)}"}
        if not stream:
            if abnormal_data == "":
                # 无异常数据，无法生成主动问答
                return {
                    "status": 200,
                    "message": "无异常",
                    "data": {}
                }
            else:
                # 根据异常数据生成相关问答问题
                # input = f"请围绕异常指标提出5个相关的问题，根据不同异常指标的严重情况，按优先级排序进行返回，回答要简短，只回答问题，不要有多余的字和符号。异常指标:{abnormal_data}"
                # question_example = """
                #                 之前得过什么重大疾病吗？比如心脏病、糖尿病、高血压，有没有做过手术？
                #                 最近几个月睡眠质量怎么样？入睡困难吗？每晚大概能睡几个小时？
                #                 最近饮食有没有突然改变？比如食欲下降、挑食，或者特别想吃某种食物？
                #                 过去有没有哮喘、过敏性鼻炎这类呼吸道疾病？最近有没有接触过花粉、宠物等过敏原？
                #                 日常运动量多吗？是经常运动，还是长时间坐着或躺着？
                #                 以前出现过类似的不舒服吗？当时是怎么治疗的？
                #                 最近工作或生活压力大不大？有没有经常感到焦虑、抑郁？
                #                 大小便规律吗？有没有出现过便血、尿液颜色异常等情况？
                #                 家族里有没有人得过遗传性疾病，像癌症、阿尔茨海默病？
                #                 最近有没有频繁熬夜、酗酒、抽烟等不良习惯？
                #                 """
                # 上述格式样例可能会被模型当作真实数据，影响问题生成，所以注释掉了
                question_example = """
                                                    xxxxxxxxxxxxxx？
                                                    xxxxxxxxxxxxxxxxxx？ 
                                                    xxxxxxxxxxxxx？
                                                    xxxxxxxxxxxxxxxxx？
                                                    xxxxxxxxxxxxxxxxxxxxxxxx？
                                                    """
                input = f"请根据以下异常指标{abnormal_data}生成5个针对性问诊问题，问题格式如下:{question_example},问题内容要求覆盖症状、病史和生活习惯，并且根据不同异常指标的严重情况，按优先级排序,不要有其它多余的字和符号。"
                messages = [
                    {
                        'role': 'system',
                        'content': '你现在的身份是一名自身的问诊专家，请根据异常数据生成相关的问诊问题'
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
                logger.info(f"user_id:{user_id}")
                logger.info(f"  ques:,{ques}")
                print("ques:", ques)
                ###########################################
                question_list = get_question(abnormal_data)
                print("question_list:", question_list)
                return {
                    "status": 200,
                    "user_id": user_id,
                    "message": "您好，关于您的hra报告，我们检查到有异常数据，需要向您询问几个问题：",
                    "data": {
                        "que_ans": ques.split("\n")
                    }
                }

        # 流式 生成主动问答
        else:
            # 流式处理逻辑
            if abnormal_data == "":
                # 无异常数据，无法生成主动问答
                return EventSourceResponse([
                    {"data": json.dumps({"type": "final_response", "content": {
                        "status": 200,
                        "message": "无异常数据",
                        "data": {}
                    }}, ensure_ascii=False)}
                ])
            else:
                # 根据异常数据生成相关问答问题
                # input = f"请围绕异常指标提出5个相关的问题，根据不同异常指标的严重情况，按优先级排序进行返回，回答要简短，只回答问题，不要有多余的字和符号。异常指标:{abnormal_data}"
                # question_example = """
                #                 之前得过什么重大疾病吗？比如心脏病、糖尿病、高血压，有没有做过手术？
                #                 最近几个月睡眠质量怎么样？入睡困难吗？每晚大概能睡几个小时？
                #                 最近饮食有没有突然改变？比如食欲下降、挑食，或者特别想吃某种食物？
                #                 过去有没有哮喘、过敏性鼻炎这类呼吸道疾病？最近有没有接触过花粉、宠物等过敏原？
                #                 日常运动量多吗？是经常运动，还是长时间坐着或躺着？
                #                 以前出现过类似的不舒服吗？当时是怎么治疗的？
                #                 最近工作或生活压力大不大？有没有经常感到焦虑、抑郁？
                #                 大小便规律吗？有没有出现过便血、尿液颜色异常等情况？
                #                 家族里有没有人得过遗传性疾病，像癌症、阿尔茨海默病？
                #                 最近有没有频繁熬夜、酗酒、抽烟等不良习惯？
                #                 """
                # 上述格式样例可能会被模型当作真实数据，影响问题生成，所以注释掉了
                question_example = """
                                                    xxxxxxxxxxxxxx？
                                                    xxxxxxxxxxxxxxxxxx？ 
                                                    xxxxxxxxxxxxx？
                                                    xxxxxxxxxxxxxxxxx？
                                                    xxxxxxxxxxxxxxxxxxxxxxxx？
                                                    """
                input = f"请根据以下异常指标{abnormal_data}生成5个针对性问诊问题，问题格式如下:{question_example},问题内容要求覆盖症状、病史和生活习惯，并且根据不同异常指标的严重情况，按优先级排序,不要有其它多余的字和符号。"
                messages = [
                    {
                        'role': 'system',
                        'content': '你现在的身份是一名自身的问诊专家，请根据异常数据生成相关的问诊问题'
                    },
                    {
                        'role': 'user',
                        'content': input
                    },
                ]

                # 流式生成问题
                async def stream_question_generator():
                    full_content = ""
                    async for part in await client.chat.completions.create(
                            model=modelName,
                            messages=messages,
                            stream=True,
                            temperature=temperature
                    ):
                        if part.choices and part.choices[0].delta.content:
                            content = part.choices[0].delta.content
                            full_content += content
                            '''yield {
                                "data": json.dumps({"type": "question_chunk", "content": content}, ensure_ascii=False)}'''

                    # 生成完整问题列表后返回最终响应
                    question_list = get_question(abnormal_data)
                    final_response = {
                        "status": 200,
                        "user_id": user_id,
                        "message": "您好，关于您的hra报告，我们检查到有异常数据，需要向您询问几个问题：",
                        "data": {
                            "que_ans": full_content.split("\n")
                        }
                    }
                    yield {
                        "data": json.dumps({"type": "final_questions", "content": final_response}, ensure_ascii=False)}

                return EventSourceResponse(stream_question_generator())

    # que _ans格式
    que_anss = [
        "question:您是否有呼吸困难的症状？;answer:出现过",
        "question:您是否有腹部疼痛或不适？;answer:被诊断出亢进",
        "question:您是否有心悸或胸痛的感觉？;answer:没有长期服用，偶尔",
        "question:您是否有头痛或视力模糊？;answer:没有",
        "question:您是否有四肢无力或感觉异常;answer:并没有"
    ]

    # 调用hra解析  分析que_ans
    try:
        # sql_helper = SQLHelper()  # 初始化 SQLHelper 类
        # 从数据库中获取该用户的最新hra_json_data
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

        # 检索逻辑
        source = retrieval(kbId=kbId, query=query, limit=limit)
        result_files = source.get("files", [])
        if not result_files:
            logger.info('检索结果为空')
        else:
            logger.info(f"检索到 {len(result_files)} 个文件")

        logger.info(f"这是给模型传递的hra报告信息{hra_result_str}")
        logger.info(f"这是给模型传递的问诊信息{que_ans}")

        # 验证历史对话格式
        valid_history = []
        for msg in history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                valid_history.append(msg)
            else:
                logger.warning(f"跳过非法历史消息: {msg}")

        input_prompt = f"请依据检索结果、问诊信息和HRA报告，生成便于用户个人可以理解的一段话术，兼顾专业与通俗易懂。按风险的高低依次解读报告中提到的各个系统的风险。解读各个系统的风险时，要参考各个系统对应的器官值进行阐述，风险较大时要明确值得大小，要解读超出正常值范围的生化指标、激素水平、例子分析中的值，进行专业的分析，明确需要进一步检查的项目，并在解读过程中对于报告中常见的医学术语要进行简单的说明。最后，请拟定一份适合他这个年龄段以及他的疾病的饮食建议以及运动处方，不要各个系统分别阐述。，若检索结果无参考价值，忽略检索内容进行作答，不要生成逗号句号之外的标点符号，也不要生成换行符\n。检索结果: {result_files}\n问诊信息: {que_ans}\n用户HRA数据: {hra_result_str}\n用户要求：{query}"
        logger.info(f"问题: {input_prompt}")

        messages = [
            {
                'role': 'system',
                'content': '你现在的身份是惠斯安普公司开发的医疗助手大模型，能够根据病人情况给出诊疗建议。'
            },
            {
                'role': 'user',
                'content': input_prompt
            },
        ]
        # 将history中的字典数据插入到messages列表的第二个位置
        messages[1:1] = valid_history
        logger.info(f"完整的对话消息: {messages}")
        logger.info(f"发送给OpenAI的messages: {json.dumps(messages, ensure_ascii=False)}")

        if stream:
            # 流式处理逻辑
            async def stream_generator():
                # 先发送初始消息
                yield {
                    "data": json.dumps({
                        "type": "initial_message",
                        "content": "正在为您分析HRA报告，请稍候..."
                    }, ensure_ascii=False)
                }

                # 流式生成回答
                async for part in await client.chat.completions.create(
                        model=modelName,
                        messages=messages,
                        stream=True,
                        temperature=temperature,
                        max_tokens=4096,
                        stream_options={"include_usage": True}
                ):
                    if part.choices and part.choices[0].delta.content:
                        content = part.choices[0].delta.content
                        yield {
                            "data": json.dumps({
                                "type": "answer_chunk",
                                "content": content
                            }, ensure_ascii=False)
                        }

                # 处理检索结果
                yield {
                    "data": json.dumps({
                        "type": "final_files",
                        "content": result_files
                    }, ensure_ascii=False)
                }

            return EventSourceResponse(stream_generator())

        else:
            # 非流式处理逻辑（直接返回完整结果）
            response = await client.chat.completions.create(
                model=modelName,
                messages=messages,
                stream=False,
                temperature=temperature
            )
            full_content = response.choices[0].message.content

            # full_content = re.sub(r'<think>.*?</think>', '', full_content)
            # full_content = re.sub(r'<think>|</think>', '', full_content)
            logger.info(full_content)

            return {
                "status": 200,
                "response": {
                    "answer": full_content,
                    "files": result_files
                }
            }

    except Exception as e:
        logger.error(f"HRA分析过程中出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
    print(user_id, "  ", temperature, "  stream:", stream, "   history:", history, "   que_ans:", que_ans)
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
    print(que_ans)
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
        # 从数据库中获取该用户的最新hra_json_data
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
