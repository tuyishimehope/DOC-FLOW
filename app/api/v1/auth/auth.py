from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.service.auth.auth import create_user, delete_user_by_id, get_all_users, update_user
from app.db.dependencies import get_db_session
from app.service.auth.schema import CreateUserRequest, UserResponse, UserUpdate
from app.service.auth.auth import create_access_token, verify_password
from app.service.auth.schema import Token
from app.models import schema
from app.service.auth.auth import CurrentUser
from config import settings


router = APIRouter(prefix="/api/v1/users", tags=["users"])


# @router.post("/login")
# async def login(login_info: LoginRequest, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
#     result = await authenticate(login_info, db_session)
#     if result is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Email or Password is not correct")
#     return result


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(schema.User).where(
            func.lower(schema.User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: CurrentUser
):
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: CreateUserRequest, db_session: AsyncSession = Depends(get_db_session)):
    try:
        result = await create_user(db_session=db_session, first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password)
        if result:
            return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


@router.get("/")
async def get_all(current_user: CurrentUser, db_session: Annotated[AsyncSession, Depends(get_db_session)], limit: int = Query(default=10, ge=1, le=100),
                  page: int = Query(default=1, ge=1)):
    result, total = await get_all_users(limit, page, db_session)
    return {"users": result, "total": total}


@router.patch("/{id}")
async def update_user_info(id: int, user_info: UserUpdate, current_user: CurrentUser, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await update_user(id, user_info, current_user, db_session)
    if result is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to perform this action")
    return result


@router.delete("/{id}")
async def delete_user(id: int, current_user: CurrentUser, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await delete_user_by_id(id, current_user, db_session)
    if result is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to perform this action")
    return result
