from app.models.schema import User
from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select


async def authenticate(email: str, password: str, db_session: AsyncSession,):
    try:
        statement = Select(User).where(User.email == email)
        results = await db_session.execute(statement)
        user_obj = results.scalar_one_or_none()
        if user_obj is None:
            raise

        ph = PasswordHasher()

        result = ph.verify(user_obj.password_hash, password)

        if result == False:
            raise

        if email == user_obj.email:
            return user_obj.email
    except Exception as e:
        raise e


async def create_user(first_name: str, last_name: str, email: str, password: str, db_session: AsyncSession,) -> bool:
    try:
        ph = PasswordHasher()

        hashed = ph.hash(password)

        password_hash = hashed
        user = User(first_name=first_name, last_name=last_name,
                    email=email, password_hash=password_hash)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return True
    except Exception as e:
        print(e)
        await db_session.rollback()
        raise e
