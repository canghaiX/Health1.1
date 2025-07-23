#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "mysql+pymysql://hsap:yanshandaxue@localhost:3306/hsap"
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=20,       # 常规连接数
#     max_overflow=10,    # 突发额外连接
#     pool_pre_ping=True, # 自动检测失效连接
#     pool_recycle=3600   # 1小时回收连接（防MySQL 8小时断开）
# )

# SessionLocal = sessionmaker(autoflush=False, bind=engine)


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 异步MySQL配置（使用aiomysql驱动）
DATABASE_URL = "mysql+aiomysql://hsap:yanshandaxue@localhost:3306/hsap"

# 创建异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,        # 常规连接数
    max_overflow=10,     # 突发额外连接
    pool_pre_ping=True,  # 自动检测失效连接
    pool_recycle=3600,   # 1小时回收连接
    echo=True            # 显示执行的SQL（调试用）
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False
)




