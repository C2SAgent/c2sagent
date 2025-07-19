# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from model.model_timeseries import Base
import os

DATABASE_URL = "postgresql+asyncpg://postgres:postgre@localhost/timeseries"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    """初始化数据库，创建表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session():
    """获取数据库会话"""
    async with async_session() as session:
        yield session