from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from app.service.auth.auth import authenticate, create_user
from app.db.dependencies import get_db_session
from app.service.auth.schema import LoginRequest, CreateUserRequest, UserResponse
from app.service.auth.auth import create_access_token, verify_password
from app.service.auth.schema import Token
from app.models import schema
from config import settings
from app.service.auth.auth import CurrentUser

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_info: LoginRequest, db_session: AsyncSession = Depends(get_db_session)):
    result = await authenticate(db_session=db_session, login_info=login_info)
    if result:
        return {"email": result}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Email or password is not correct")


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


@router.get("/me")
async def get_current_user(
    current_user: CurrentUser
):
    return current_user


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: CreateUserRequest, db_session: AsyncSession = Depends(get_db_session)):
    try:
        result = await create_user(db_session=db_session, first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password)
        if result:
            return UserResponse(id=result.id, first_name=result.first_name, last_name=result.last_name, email=result.email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")
