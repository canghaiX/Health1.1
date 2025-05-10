# app/models.py
import hashlib
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

# 上面的例子只是展示了模型可以做什么的冰山一角。模型具有以下方法和属性：
# dict()返回模型字段和值的字典；参看。导出模型json()返回一个JSON字符串表示dict()；参看。导出模型copy()返回模型的副本（默认为浅拷贝）；参看。导出模型
# parseobj()如果对象不是字典，则用于将任何对象加载到具有错误处理的模型中的实用程序；参看。辅助函数
# parseraw()用于加载多种格式字符串的实用程序；参看。辅助函数
# parsefile()喜欢parseraw()但是对于文件路径；参看。辅助函数fromorm()将数据从任意类加载到模型中；参看。ORM模式
# schema()返回将模型表示为JSONSchema的字典；参看。图式schemajson()schema()
# 返回;的JSON字符串表示形式参看。图式
# construct()无需运行验证即可创建模型的类方法；参看。创建没有验证的模型
# `__fields_set初始化模型实例时设置的字段名称集__fields模型字段的字典__config`模型的配置类，cf。模型配置


class DocumentResponse(BaseModel):
    page_content: str
    metadata: dict


class DocumentModel(BaseModel):
    page_content: str
    metadata: Optional[dict] = {}

    def generate_digest(self):
        hash_obj = hashlib.md5(self.page_content.encode())
        return hash_obj.hexdigest()


class StoreDocument(BaseModel):
    filepath: str
    filename: str
    file_content_type: str
    file_id: str


class QueryRequestBody(BaseModel):
    query: str
    file_id: str
    k: int = 4
    entity_id: Optional[str] = None


class CleanupMethod(str, Enum):
    incremental = "incremental"
    full = "full"


class QueryMultipleBody(BaseModel):
    query: str
    file_ids: List[str]
    k: int = 4
