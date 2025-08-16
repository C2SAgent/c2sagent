from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# 使用异步引擎 - 注意URL要以 asyncpg 或 aiomysql 开头
# 例如：postgresql+asyncpg://user:password@localhost/dbname
engine = create_async_engine(settings.DATABASE_URL, echo=True)  # 可选，用于调试显示SQL语句

# 创建异步会话工厂
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 异步会话通常需要设置这个
)

Base = declarative_base()


async def get_db():
    """
    异步数据库会话生成器
    使用方式：
    async with get_db() as db:
        # 使用db会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
