from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.service.auth.auth import authenticate, create_user
from app.db.dependencies import get_db_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/authenticate")
async def login(email: str, password: str, db_session: AsyncSession = Depends(get_db_session)):
    try:
        result = await authenticate(db_session=db_session, email=email, password=password)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email or password not correct")


@router.post("/signup")
async def signup(first_name: str = Body(), last_name: str = Body(), email: str = Body(), password: str = Body(), db_session: AsyncSession = Depends(get_db_session)):
    try:
        # validation
        result = await create_user(db_session=db_session, first_name=first_name, last_name=last_name, email=email, password=password)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Failed")
