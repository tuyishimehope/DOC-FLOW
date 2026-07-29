from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import User


async def get_user_by_email(email: str, db_session: AsyncSession) -> User | None:
    statement = select(User).where(User.email == email)
    results = await db_session.execute(statement)
    user_obj = results.scalar_one_or_none()
    return user_obj


async def get_user_by_id(id: int, db_session: AsyncSession) -> User | None:
    statement = select(User).where(User.id == id)
    results = await db_session.execute(statement)
    user_obj = results.scalar_one_or_none()
    return user_obj


async def get_users(limit: int, skip: int, db_session: AsyncSession) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    result = await db_session.execute(statement)
    data = result.scalars().all()
    return list(data)


async def get_count_users(db_session: AsyncSession) -> int:
    statement = select(func.count()).select_from(User)
    result = await db_session.execute(statement)
    data = result.scalar_one()
    return data


