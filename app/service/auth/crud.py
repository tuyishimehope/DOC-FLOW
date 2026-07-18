from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import User

async def get_user_by_email(email: str, db_session: AsyncSession):
    statement = Select(User).where(User.email == email)
    results = await db_session.execute(statement)
    user_obj = results.scalar_one_or_none()
    return user_obj
