from fastapi import APIRouter, Depends, HTTPException
#from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime
from app.database.utils import get_db
from app.models import  HraData
from app.models.qadata import QaData
from app.routers.rag_knowledge import retrieval
from sqlalchemy import select

# 导入处理函数
from app.utils.hra_json_filter_new import hra_json_filter, get_abnormal_data, get_question

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 请求模型
class HRAReportRequest(BaseModel):
    user_id: int
    kbId: Optional[str] = "1"
    report_interpret: bool

# 响应模型 - 修复字段名
class SystemInterpretation(BaseModel):
    system_name: str
    interpretation: str
    questions: str  # 修改为 questions 匹配文档要求

class HRAReportResponse(BaseModel):
    code: int
    message: str
    data: List[SystemInterpretation]

# 知识库检索函数
async def knowledge_base_search(query: str, kb_id: str = "1") -> str:
    """
    知识库检索逻辑
    
    Args:
        query: 检索查询内容
        kb_id: 知识库ID
        
    Returns:
        str: 检索到的相关知识内容
    """
    kb_id = '1'
    try:
        result = await retrieval(kb_id, query)
        return result
    except Exception as e:
        logger.error(f"知识库检索失败: {e}")
        return ""

# 模型调用函数
async def call_llm_for_interpretation(system_name: str, abnormal_indicators: List[Dict], 
                                    system_description: str, knowledge_context: str) -> str:
    """
    LLM调用逻辑 - 这里需要根据你的实际LLM接口实现
    
    Args:
        system_name: 系统名称
        abnormal_indicators: 异常指标列表
        system_description: 系统状态描述
        knowledge_context: 知识库检索到的相关内容
        
    Returns:
        str: 模型生成的解读内容
    """
    # 构建提示词
    prompt = f"""
    作为专业的医疗健康分析师，请根据以下HRA检测数据为患者提供系统性的健康解读：

    系统名称：{system_name}
    异常指标详情：
    """
    
    for indicator in abnormal_indicators:
        prompt += f"- {indicator['指标名称']}：{indicator['数值']}\n"
    
    if system_description:
        prompt += f"\n系统状态说明：{system_description}\n"
    
    if knowledge_context:
        prompt += f"\n相关医学知识：{knowledge_context}\n"
    
    prompt += """
    请根据以上信息：
    1. 简要说明各异常指标的含义
    2. 分析可能的健康风险
    3. 提供初步的健康建议
    4. 用专业但通俗易懂的语言表达，控制在200字以内

    注意：仅做健康指导，不替代专业医疗诊断。
    """
    
    # TODO: 这里需要替换为你的实际LLM调用
    # 例如：response = await your_llm_api_call(prompt)
    
    # 临时返回示例（需要替换为真实的模型调用）
    indicators_text = "、".join([f"{item['指标名称']}({item['数值']})" for item in abnormal_indicators])
    return f"您的{system_name}检测中发现以下异常指标：{indicators_text}。建议您关注相关健康状况，必要时咨询专业医师进行进一步检查。"

# 数据库操作函数
async def get_hra_data_by_user_id(db: AsyncSession, user_id: int) -> Dict:
    """
    从数据库获取用户HRA报告数据
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        Dict: HRA报告数据字典
    """
    try:
        # 使用异步查询方法
        result = await db.execute(
            select(HraData).filter(HraData.user_id == user_id)
        )
        hra_record = result.first()    

        if not hra_record:
            logger.warning(f"未找到用户 {user_id} 的HRA报告")
            return None

        return json.loads(hra_record[0].hra_data)
    except Exception as e:
        logger.error(f"获取HRA报告数据失败: {e}")
        return None
    

async def save_hra_interpretation_summary(db: AsyncSession, user_id: int, interpretation_summary: str):
    """
    保存HRA解读汇总到数据库
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        interpretation_summary: 解读汇总内容
    """
    try:
        qa_record = QaData(
            user_id=user_id,
            hra_report_data=interpretation_summary,
            created_at=datetime.now()
        )
        db.add(qa_record)
        await db.commit()  # 异步提交
        logger.info(f"成功保存用户 {user_id} 的HRA解读汇总")
    except Exception as e:
        await db.rollback()  # 异步回滚
        logger.error(f"保存HRA解读汇总失败: {e}")
        raise

@router.post("/knowledge_base_chat_with_hra/", response_model=HRAReportResponse)
async def hra_report_interpretation(
    request: HRAReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    HRA报告解析接口
    
    根据用户HRA报告数据和知识库进行RAG检索问答，生成系统解读报告
    """
    try:
        # 1. 参数验证
        if not request.report_interpret:
            raise HTTPException(status_code=400, detail="report_interpret must be True")
        
        # 2. 从数据库获取用户HRA报告数据 - 修复：添加 await
        logger.info(f"开始获取用户 {request.user_id} 的HRA报告数据")
        hra_raw_data = await get_hra_data_by_user_id(db, request.user_id)
        
        if not hra_raw_data:
            raise HTTPException(status_code=404, detail="未找到该用户的HRA报告数据")
        
        # 3. 使用过滤函数处理HRA数据
        logger.info("开始处理HRA报告数据")
        processed_data = hra_json_filter(hra_raw_data)
        
        # 4. 生成各系统解读报告
        interpretation_results = []
        interpretation_summary_parts = []
        
        for system_name, system_data in processed_data["系统检查结果"].items():
            # 只处理有异常的系统
            if system_data["状态"] == "异常" and system_data["异常指标"]:
                logger.info(f"开始处理异常系统: {system_name}")
                
                # 获取系统状态描述
                system_description = processed_data["系统状态说明"].get(system_name, "")
                
                # 构建知识库检索查询
                abnormal_indicators_text = ", ".join([
                    item["指标名称"] for item in system_data["异常指标"]
                ])
                search_query = f"{system_name} {abnormal_indicators_text} 健康解读"
                
                # 调用知识库检索
                try:
                    knowledge_context = await knowledge_base_search(search_query, request.kbId)
                except Exception as e:
                    logger.warning(f"知识库检索失败: {e}")
                    knowledge_context = ""
                
                # 调用LLM生成解读
                try:
                    interpretation = await call_llm_for_interpretation(
                        system_name=system_name,
                        abnormal_indicators=system_data["异常指标"],
                        system_description=system_description,
                        knowledge_context=knowledge_context
                    )
                except Exception as e:
                    logger.error(f"LLM调用失败: {e}")
                    # 提供默认解读
                    abnormal_list = [f"{item['指标名称']}({item['数值']})" 
                                   for item in system_data["异常指标"]]
                    interpretation = f"{system_name}检测中发现以下异常指标：{', '.join(abnormal_list)}。建议您关注相关健康状况，必要时咨询专业医师进行进一步检查。"
                
                # 生成相关问题
                try:
                    # 将异常指标转换为get_question函数需要的格式
                    abnormal_data_for_questions = []
                    for item in system_data["异常指标"]:
                        abnormal_data_for_questions.append({item["指标名称"]: item["数值"]})
                    
                    questions_list = get_question(abnormal_data_for_questions)
                    question = questions_list[0] if questions_list else ""
                except Exception as e:
                    logger.warning(f"生成问题失败: {e}")
                    question = ""
                
                # 构建结果 - 修复：使用 questions 字段名
                system_result = SystemInterpretation(
                    system_name=system_name,
                    interpretation=interpretation,
                    questions=question  # 修改为 questions
                )
                interpretation_results.append(system_result)
                
                # 为汇总准备内容
                interpretation_summary_parts.append(f"{system_name}: {interpretation}")
        
        # 5. 如果没有异常系统，返回正常状态
        if not interpretation_results:
            interpretation_results.append(SystemInterpretation(
                system_name="整体评估",
                interpretation="恭喜您！本次HRA检测中各项指标均在正常范围内，请继续保持良好的生活方式和健康习惯。",
                questions=""  # 修改为 questions
            ))
            interpretation_summary = "本次HRA检测结果整体正常，各系统功能良好。"
        else:
            # 6. 生成解读汇总并保存到数据库
            interpretation_summary = "\n".join(interpretation_summary_parts)
            
        try:
            # 修复：添加 await
            await save_hra_interpretation_summary(db, request.user_id, interpretation_summary)
            logger.info(f"已保存用户 {request.user_id} 的HRA解读汇总")
        except Exception as e:
            logger.error(f"保存解读汇总失败: {e}")
        
        # 7. 返回结果
        response = HRAReportResponse(
            code=200,
            message="成功获取HRA报告解读",
            data=interpretation_results
        )
        
        logger.info(f"成功完成用户 {request.user_id} 的HRA报告解析")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HRA报告解析过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请联系管理员")

# 健康检查接口
@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}