from fastapi import APIRouter, UploadFile, HTTPException, status, Body

from app.service.document.document import process_document
from app.service.document.schema import Processing_Type
from utils.document import valid_type_document

router = APIRouter(prefix="/document",tags=["document"])

@router.post("")
async def post_document(file: UploadFile, processing_type: Processing_Type = Body(), instructions: str= Body()):
    result = valid_type_document(file=file)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File Format Not Accepted")
    
    return await process_document(file=file, processing_type=processing_type, instructions=instructions)

@router.get("/document/{id}")
async def get_document(id: int):
    return

@router.get("")
async def get_documents():
    return

@router.delete("/document/{id}")
async def delete_document(id: int):
    return