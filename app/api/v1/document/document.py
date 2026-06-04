from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.service.document.document import process_document
from app.service.document.schema import Processing_Type
from utils.document import valid_type_document

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
    return

@router.delete("/document/{id}")
async def delete_document(id: int):
    return