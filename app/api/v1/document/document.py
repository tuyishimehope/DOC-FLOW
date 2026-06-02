from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.service.document.document import delete_document, get_document, get_documents, get_status_jobs, process_document
from app.service.document.schema import Processing_Type
from app.utils.document import valid_type_document
from app.service.auth.auth import CurrentUser

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_document_endpoint(file: UploadFile, current_user: CurrentUser, processing_type: Processing_Type = Body(), instructions: str = Body(), db_session: AsyncSession = Depends(get_db_session)):
    result = valid_type_document(file=file)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File Format Not Accepted")

    response = await process_document(id=current_user.id, file=file, processing_type=processing_type, instructions=instructions, db_session=db_session)
    return response


@router.get("/{id}")
async def get_document_endpoint(id: int, current_user: CurrentUser, db_session: AsyncSession = Depends(get_db_session)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to view document")

    document = await get_document(id=id, db_session=db_session, user_id=current_user.id)
    if document is not None:
        return document

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Document Not Found")


@router.get("")
async def get_documents_endpoint(current_user: CurrentUser, page: int = Query(default=1, title="Current page", description="The current page to display items"), limit: int = Query(default=10, title="limit", description="limit of items per page", gt=1, le=50),  db_session: AsyncSession = Depends(get_db_session)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to view document")
    result, total_documents = await get_documents(page=page, limit=limit, db_session=db_session, user_id=current_user.id)
    return {"data": result, "total_documents": total_documents}


@router.delete("/{id}")
async def delete_document_endpoint(current_user: CurrentUser, id: int, db_session: AsyncSession = Depends(get_db_session)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to view document")

    document = await delete_document(id=id, db_session=db_session, current_user=current_user)
    if document is not None:
        return document

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Document Not Found")


@router.get("/{id}/jobs")
async def get_status_jobs_endpoint(id: int, db_session: AsyncSession = Depends(get_db_session)):
    response = await get_status_jobs(id=id, db_session=db_session)
    if response is not None:
        return [{"attempt": data.attempt_number, "status": data.status, "created_at": data.started_at, "completed_at": data.completed_at} for data in response]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
