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


# 配置类
class Settings():
    # doubao平台模型调用
    ARK_API_KEY = "9bddecca-cf12-4d34-9991-f190191bc420"
    ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    DOUBA_MODEL = "doubao-1-5-thinking-pro-250415"

    # 业务配置
    TIMEOUT_SECONDS = 10
    SUMMARY_PROMPT = "请用一段话总结以上对话内容："

    # MySQL 数据库配置
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    # MYSQL_USER: str = "root"
    # MYSQL_PASSWORD: str = "root"
    # MYSQL_DATABASE: str = "health"
    #以下为111服务器配置
    MYSQL_USER: str = "hsap"
    MYSQL_PASSWORD: str = "666666"
    MYSQL_DATABASE: str = "health_data"

    @property
    def database_url(self) -> str:
        """生成SQLAlchemy连接URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    class Config:
        env_file = ".env"  # 可选：从.env文件加载配置
        env_file_encoding = "utf-8"
# mysql配置实例
settings = Settings()  # 全局配置实例

# 日志相关配置
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = logging.DEBUG  #记录所有级别的log
LOG_DIR = LOGGER_DIR 
LOG_FILE = "app.log"  
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50MB
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