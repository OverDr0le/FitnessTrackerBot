from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from configs.config_reader import config
from database.models import Base

engine = create_async_engine(config.db_lite.get_secret_value(), echo = False)

session_maker = async_sessionmaker(bind = engine, class_= AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
