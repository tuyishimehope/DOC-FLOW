from fastapi import UploadFile
import traceback
from sqlalchemy.ext.asyncio import AsyncSession


from app.tasks.document_task import start_processing
from app.utils.document import get_file_extension
from .schema import Processing_Type
from app.service.document.schema import Processing_status, Processing_Type
from app.service.file.file import post_file, get_file
from app.service.document.crud import delete_document_by_id, get_all_documents, get_document_by_id, get_file_id, get_jobs, get_processing_request_result, get_processing_request_status, save_document, save_file, save_processing_request, get_total_no_of_documents, get_processing_request_by_id


async def process_document(file: UploadFile, processing_type: Processing_Type, instructions: str, db_session: AsyncSession):
    try:
        file_name = get_file_extension(file)

        file_object = await save_file(file=file, file_name=file_name, db_session=db_session)

        await post_file(file=file, file_id=str(file_object.id))

        document_object = await save_document(file=file, file_object=file_object, db_session=db_session)

        processing_request_object = await save_processing_request(document_object=document_object, processing_type=processing_type, instructions=instructions, db_session=db_session)

        if processing_request_object is None:
            return

        start_processing.delay(
            processing_request_id=processing_request_object.id)

        processing_request_object.status = Processing_status.QUEUED
        await db_session.commit()

        return {"processing_request_id": processing_request_object.id, "status": processing_request_object.status}
    except Exception as e:
        traceback.print_exc()
        print("An expected error occurred", e)
        await db_session.rollback()


async def get_processing_status(
    processing_request_id: int,
    db_session: AsyncSession
):
    result = await get_processing_request_status(processing_request_id=processing_request_id, db_session=db_session)

    if not result:
        return None

    return {
        "id": result.id,
        "status": result.status
    }


async def get_processing_result(
    processing_request_id: int,
    db_session: AsyncSession
):
    result = await get_processing_request_result(processing_request_id=processing_request_id, db_session=db_session)

    if not result:
        return None

    return result.content_json


async def get_document(id: int, db_session: AsyncSession):
    result = await get_document_by_id(id=id, db_session=db_session)
    return result


async def get_documents(page: int, limit: int, db_session: AsyncSession):
    result = await get_all_documents(page=page, limit=limit, db_session=db_session)
    total_documents = await get_total_no_of_documents(db_session=db_session)
    total_documents_per_page = total_documents % limit
    return result, total_documents, total_documents_per_page


async def delete_document(id: int, db_session: AsyncSession):
    return await delete_document_by_id(id=id, db_session=db_session)


async def get_file_by_id(id: int, db_session: AsyncSession):

    file_record = await get_file_id(id=id, db_session=db_session)

    if not file_record:
        return None

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


async def get_status_jobs(id: int, db_session: AsyncSession):
    response = await get_jobs(id=id, db_session=db_session)
    return response


async def get_processing_request(id: int, db_session: AsyncSession):
    response = await get_processing_request_by_id(id, db_session)
    return response
