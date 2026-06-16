from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.service.document.document import get_file_by_id

router = APIRouter(prefix="/file", tags=["file"])


@router.get("/{id}", status_code=status.HTTP_200_OK, summary="Get a file by id", description="You can get a file by id", responses={
    200: {
            "content": {
                "application/pdf": {}
            }
            }
})
async def get_file_endpoint(id: int, db_session: AsyncSession = Depends(get_db_session)):
    """
    Get a file by id

    Args:
        id (int): id of the file
        db_session (AsyncSession, optional): db session. Defaults to Depends(get_db_session).

    Raises:
        HTTPException: return expection when the file not found

    Returns:
        file: Returns a file 
    """
    result = await get_file_by_id(id=id, db_session=db_session)

    if result:
        return Response(
            content=result["content"],
            media_type=result["content_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{result["name"]}"'
            }
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="file not found")
