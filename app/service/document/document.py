from datetime import datetime
from fastapi import UploadFile
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.tasks.document_task import start_processing

from .schema import Processing_Type
from app.service.openai.service import OpenaiService
from app.models.schema import Document, File, Processing_Request, Extracted_Result, Processing_Job
from app.service.document.schema import Processing_status, Processing_Type, Processing_Job_Status
from app.service.file.file import post_file, get_file




def get_file_extension(file: UploadFile) -> str:
    if file.filename is None:
        raise ValueError("Uploaded file has no filename")

    return Path(file.filename).suffix.lstrip(".")


async def process_document(file: UploadFile, processing_type: Processing_Type, instructions: str, db_session: Session):
    try:
        file_name = get_file_extension(file)

        file_object = File(name=file.filename,
                           content_type=file.content_type, extension=file_name)

        db_session.add(file_object)
        db_session.flush()
        
        result = await post_file(file=file, file_id=str(file_object.id))

        document_object = Document(name=file.filename, file=file_object)

        db_session.add(document_object)
        db_session.flush()
                

        processing_request_object = Processing_Request(
            document_id=document_object.id, processing_type=processing_type, instructions=instructions, status=Processing_status.PENDING)

        db_session.add(processing_request_object)
        db_session.commit()

        start_processing.delay(
            processing_request_id=processing_request_object.id)

        processing_request_object.status = Processing_status.QUEUED
        db_session.commit()

        return {"processing_request_id": processing_request_object.id, "status": processing_request_object.status}
    except Exception as e:
        print("An expected error occurred", e)
        db_session.rollback()




def get_processing_status(
    processing_request_id: int,
    db: Session
):
    request = (
        db.query(Processing_Request)
        .filter(
            Processing_Request.id == processing_request_id
        )
        .first()
    )

    if not request:
        return None

    return {
        "id": request.id,
        "status": request.status
    }


def get_processing_result(
    processing_request_id: int,
    db: Session
):
    result = (
        db.query(Extracted_Result)
        .filter(
            Extracted_Result.processing_request_id
            == processing_request_id
        )
        .first()
    )

    if not result:
        return None

    return result.content_json


async def get_document(id: int):
    return


async def get_documents():
    return


async def delete_document(id: int):
    return
