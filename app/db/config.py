from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends
from typing import AsyncGenerator, Annotated
from decouple import config

DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_NAME = config("DB_NAME")
DB_PORT = config("DB_PORT", cast=int)
DB_HOST = config("DB_HOST")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@localhost:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]




