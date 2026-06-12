from sqlalchemy.ext.asyncio import (
    async_sessionmaker
)

from app.db.engine import engine

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)