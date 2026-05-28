import io

from fastapi import UploadFile

from .schema import ProcessingType
from app.tasks.tasks import add
from app.service.openai.service import OpenaiService

def extract_text_from_pdf(file_path):
    from pypdf import PdfReader
    reader = PdfReader(stream=file_path)

    page = reader.pages[0]
    return page.extract_text()

async def extract_text_from_doc(file_path: UploadFile):
    from docx import Document
    
    file_bytes = await file_path.read()
    
    file_stream = io.BytesIO(file_bytes)
    
    doc = Document(file_stream)
    
    text = [para.text for para in doc.paragraphs]
    full_text = "\n".join(text)
    
    return full_text

async def process_document(file: UploadFile, processing_type: ProcessingType, instructions: str):
    
    extracted_content = ""
    if file.content_type == "application/pdf":
        extracted_content = extract_text_from_pdf(file_path=file.file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_content = await extract_text_from_doc(file_path=file)
        
    if not extracted_content:
        return

    if processing_type == ProcessingType.DOCUMENT_SUMMARY:
        result = await OpenaiService().generate_summary(content=extracted_content, instructions=instructions)
    elif processing_type == ProcessingType.INVOICE_EXTRACTION:
        result = await OpenaiService().generate_summary(content=extracted_content, instructions=instructions)
    elif processing_type == ProcessingType.CONTRACT_METADATA:
        result = await OpenaiService().generate_summary(content=extracted_content, instructions=instructions)
    else:
        return
        
    
    return result

async def get_document(id: int):
    return

async def get_documents():
    return

async def delete_document(id: int):
    return