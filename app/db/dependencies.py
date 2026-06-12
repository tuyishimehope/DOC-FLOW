from sqlalchemy.orm import Session

from app.db.session import SessionLocal


async def get_db_session():
    db = SessionLocal()

    try:
        yield db
    finally:
        await db.close()
