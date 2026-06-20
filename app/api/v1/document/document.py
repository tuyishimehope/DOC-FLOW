from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.service.document.document import delete_document, get_document, get_documents, get_processing_result, get_processing_status, process_document
from app.service.document.schema import Processing_Type
from app.utils.document import valid_type_document

router = APIRouter(prefix="/document", tags=["document"])


@router.post("")
async def post_document_endpoint(file: UploadFile, processing_type: Processing_Type = Body(), instructions: str = Body(), db_session: AsyncSession = Depends(get_db_session)):
    result = valid_type_document(file=file)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File Format Not Accepted")

    return await process_document(file=file, processing_type=processing_type, instructions=instructions, db_session=db_session)


@router.get("/status/{processing_request_id}")
async def get_status_endpoint(
    processing_request_id: int,
    db_session: AsyncSession = Depends(get_db_session)
):
    result = await get_processing_status(
        processing_request_id,
        db_session
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Processing request with id: {processing_request_id} not found")
    return result


@router.get("/result/{processing_request_id}")
async def get_result_endpoint(
    processing_request_id: int,
    db_session: AsyncSession = Depends(get_db_session)
):
    result = await get_processing_result(
        processing_request_id,
        db_session
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Processing request with id: {processing_request_id} not found")
    return result


@router.get("/document/{id}")
async def get_document_endpoint(id: int, db_session: AsyncSession = Depends(get_db_session)):
    document = await get_document(id=id, db_session=db_session)
    if document:
        return document
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Document Not Found")


@router.get("?")
async def get_documents_endpoint(page: int = Query(default=1, title="Current page", description="The current page to display items"), limit: int = Query(default=10, title="limit", description="limit of items per page", gt=1, le=50), db_session: AsyncSession = Depends(get_db_session)):
    result, total_documents =  await get_documents(page=page, limit=limit, db_session=db_session)
    return result, total_documents


@router.delete("/document/{id}")
async def delete_document_endpoint(id: int, db_session: AsyncSession = Depends(get_db_session)):
    document = await delete_document(id=id, db_session=db_session)
    if document:
        return document
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Document Not Found")
