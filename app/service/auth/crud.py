from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import User


async def get_user_by_email(email: str, db_session: AsyncSession):
    statement = Select(User).where(User.email == email)
    results = await db_session.execute(statement)
    user_obj = results.scalar_one_or_none()
    return user_obj


async def get_user_by_id(id: int, db_session: AsyncSession):
    statement = Select(User).where(User.id == id)
    results = await db_session.execute(statement)
    user_obj = results.scalar_one_or_none()
    return user_obj


async def get_users(limit: int, page: int, db_session: AsyncSession):
    offset = (page - 1) * limit
    statement = Select(User).limit(limit).offset(offset)
    result = await db_session.execute(statement)
    data = result.scalars().all()
    return data


async def get_count_users(db_session: AsyncSession):
    statement = Select(func.count()).select_from(User)
    result = await db_session.execute(statement)
    data = result.scalars().all()
    return data


