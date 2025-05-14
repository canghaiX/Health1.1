import os

# 项目根目录（health1.1所在目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 文件存储目录
HRA_FILEBASE_DIR = os.path.join(PROJECT_ROOT, "hra_filebase")

#日志存放目录
LOGGER_DIR = os.path.join(PROJECT_ROOT, "log")

#qwen平台模型调用api_key以及url
api_key='sk-7548be9550ca4f15a8b211deddbfc9e3'
base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"



# 日志相关配置
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = "DEBUG"  #记录所有级别的log
LOG_DIR = LOGGER_DIR 
LOG_FILE = "app.log"  
MAX_LOG_SIZE = 50 * 1024 * 1024  # 10MB
BACKUP_COUNT = 10  # 保留的旧日志文件数量

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """
    获取配置好的logger实例
    
    Args:
        name: 日志器名称，通常使用__name__
    
    Returns:
        配置好的logger实例
    """
    # 创建或获取logger，使用传入的name作为标识
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(LOG_LEVEL)
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器（支持日志轮转）
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE),
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger