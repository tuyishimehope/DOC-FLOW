
from sqlalchemy import Select

from app.models.schema import Document, File
from app.service.auth.auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

async def get_file_id(id: int, current_user: CurrentUser, db_session: AsyncSession):
    stmt = Select(File).join(Document).where(File.id == id, Document.user_id == current_user.id)

    file_record = await db_session.execute(stmt)

    result = file_record.scalar_one_or_none()

    return result