from fastapi import UploadFile
from pathlib import Path
from sqlalchemy import Select
from sqlalchemy.orm import Session


from app.tasks.document_task import start_processing

from .schema import Processing_Type
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
        Select(Processing_Request)
        .where(
            Processing_Request.id == processing_request_id
        )
    )
    result = db.execute(request).scalar_one_or_none()

    if not result:
        return None

    return {
        "id": result.id,
        "status": result.status
    }


def get_processing_result(
    processing_request_id: int,
    db: Session
):
    request = (
        Select(Extracted_Result)
        .where(
            Extracted_Result.processing_request_id
            == processing_request_id
        )
    )
    result = db.execute(request).scalar_one_or_none()
    
    if not result:
        return None

    return result.content_json


async def get_document(id: int, db_session: Session):
    statement = Select(Document).where(Document.id == id)
    result = db_session.execute(statement).scalar_one_or_none()
    return result


async def get_documents(db_session: Session):
    statement = Select(Document)
    result = db_session.execute(statement).scalars().all()
    return result


async def delete_document(id: int, db_session: Session):
    try:
        document = get_document(id = id, db_session=db_session)
        if document :
            db_session.delete(document)
            db_session.commit()
    except:
        db_session.rollback()
        
async def get_file_by_id(id: int, db_session: Session):
    stmt = Select(File).where(File.id == id)

    file_record = (
        db_session.execute(stmt)
        .scalar_one_or_none()
    )

    if not file_record:
        return None
    print(file_record.name)
    response = get_file(file_id=id)

    try:
        content = response.read()
    finally:
        response.close()
        response.release_conn()

    return {
        "name": file_record.name,
        "content": content,
        "content_type": file_record.content_type
    }