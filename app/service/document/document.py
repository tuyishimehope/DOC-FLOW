from fastapi import UploadFile

from .schema import ProcessingType

async def process_document(file: UploadFile, processing_type: ProcessingType, instructions: str):
    return file.filename, processing_type, instructions

async def get_document(id: int):
    return

async def get_documents():
    return

async def delete_document(id: int):
    return