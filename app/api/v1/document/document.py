from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.service.document.document import get_processing_result, get_processing_status, process_document
from app.service.document.schema import Processing_Type
from app.utils.document import extract_text_from_pdf, valid_type_document

router = APIRouter(prefix="/document",tags=["document"])

@router.post("")
async def post_document(file: UploadFile, processing_type: Processing_Type = Body(), instructions: str= Body(), db_session: Session = Depends(get_db_session)):
    result = valid_type_document(file=file)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File Format Not Accepted")
    
    return await process_document(file=file, processing_type=processing_type, instructions=instructions, db_session=db_session)

@router.get("/document/{id}")
async def get_document(id: int):
    return

@router.get("")
async def get_documents():
    return extract_text_from_pdf(file_stream=None)

@router.delete("/document/{id}")
async def delete_document(id: int):
    return

@router.get("/status/{processing_request_id}")
async def get_status(
    processing_request_id: int,
    db_session: Session = Depends(get_db_session)
):
    return get_processing_status(
        processing_request_id,
        db_session
    )

@router.get("/result/{processing_request_id}")
async def get_result(
    processing_request_id: int,
    db_session: Session = Depends(get_db_session)
):
    return get_processing_result(
        processing_request_id,
        db_session
    )