from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.auth.auth import authenticate, create_user
from app.db.dependencies import get_db_session
from app.service.auth.schema import LoginRequest, CreateUserRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/authenticate")
async def login(login_info: LoginRequest, db_session: AsyncSession = Depends(get_db_session)):
    result = await authenticate(db_session=db_session, email=login_info.email, password=login_info.password)
    if result:
        return result
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Email or password not correct")


@router.post("/signup")
async def signup(user: CreateUserRequest, db_session: AsyncSession = Depends(get_db_session)):
    try:
        result = await create_user(db_session=db_session, first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password)
        if result:
            return UserResponse(id=result.id, first_name=result.first_name, last_name=result.last_name, email=result.email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")