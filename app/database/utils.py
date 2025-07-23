# from .session import SessionLocal

# def get_db():
#     """获取数据库会话的依赖函数"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()




#from sqlalchemy.orm import sessionmaker
#from app.database.session import AsyncSessionLocal
# async def get_db():
#     """
#     异步数据库会话依赖项
#     使用示例：
#     @router.get("/")
#     async def route(db: AsyncSession = Depends(get_db)):
#         ...
#     """
#     db = AsyncSessionLocal()
#     try:
#         yield db
#     finally:
#         await db.close()



from app.database.session import AsyncSessionLocal
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
        await db.commit()  # 请求成功时提交
    except Exception:
        await db.rollback()  # 异常时回滚
        raise
    finally:
        await db.close()