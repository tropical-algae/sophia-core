from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.common.config import settings
from sophia.core.db.models import *

local_engine = create_async_engine(
    url=settings.SQL_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    echo=settings.DEBUG,
)
LocalSession = async_sessionmaker(
    autocommit=False, autoflush=False, bind=local_engine, class_=AsyncSession
)


async def init_db_models():
    logger.info("Check SQL table structure and fix the missing.")
    async with local_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
