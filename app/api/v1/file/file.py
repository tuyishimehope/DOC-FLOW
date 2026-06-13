from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.service.document.document import get_file_by_id

router = APIRouter(prefix="/file", tags=["file"])


@router.get("/{id}")
async def get_file_endpoint(id: int, db_session: AsyncSession = Depends(get_db_session)):
    result = await get_file_by_id(id=id, db_session=db_session)

    if result:
        return Response(
            content=result["content"],
            media_type=result["content_type"],
            headers={
                "Content-Disposition": 'attachment; filename="document.pdf"'
            }
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="file not found")
