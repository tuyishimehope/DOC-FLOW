from datetime import timezone, datetime, timedelta
import jwt
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import AsyncSession


from config import settings
from app.models.schema import User
from app.service.auth.crud import get_user_by_email


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(password=plain_password, hash=hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,settings.secret_key.get_secret_value(),algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token,settings.secret_key.get_secret_value(),algorithms=[settings.algorithm],options={"require":["exp","sub"]})
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
        

async def authenticate(email: str, password: str, db_session: AsyncSession):
    try:
        user_obj = await get_user_by_email(email, db_session)
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


async def create_user(first_name: str, last_name: str, email: str, password: str, db_session: AsyncSession,) :
    try:
        password_hash = hash_password(password)
        user = User(first_name=first_name, last_name=last_name,
                    email=email.lower(), password_hash=password_hash)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    except Exception as e:
        print(e)
        await db_session.rollback()
        raise e
