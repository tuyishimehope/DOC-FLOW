from app.core.config import settings

from sqlalchemy.ext.asyncio import (
    create_async_engine,
)
from sqlalchemy import create_engine

DATABASE_NAME=settings.DATABASE_NAME
DATABASE_PASSWORD=settings.DATABASE_PASSWORD
DATABASE_HOST=settings.DATABASE_HOST
DATABASE_PORT=settings.DATABASE_PORT
DATABASE_USER=settings.DATABASE_USER


engine = create_async_engine(
    f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

sync_engine = create_engine(
    f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)
