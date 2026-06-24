from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import Document, Extracted_Result, File, Processing_Request, Processing_Job
from app.service.document.schema import Processing_status


async def save_file(file, file_name, db_session: AsyncSession):
    file_object = File(name=file.filename,
                       content_type=file.content_type, extension=file_name)

    db_session.add(file_object)
    await db_session.flush()

    return file_object


async def save_document(file, file_object, db_session: AsyncSession):
    document_object = Document(name=file.filename, file=file_object)

    db_session.add(document_object)
    await db_session.flush()

    return document_object


async def save_processing_request(document_object, processing_type, instructions, db_session: AsyncSession):
    processing_request_object = Processing_Request(
        document_id=document_object.id, processing_type=processing_type, instructions=instructions, status=Processing_status.PENDING)

    db_session.add(processing_request_object)
    await db_session.commit()

    return processing_request_object


async def get_processing_request_status(processing_request_id: int, db_session: AsyncSession):
    request = (
        Select(Processing_Request)
        .where(
            Processing_Request.id == processing_request_id
        )
    )
    result = await db_session.execute(request)
    response = result.scalar_one_or_none()
    return response


async def get_processing_request_result(processing_request_id: int, db_session: AsyncSession):
    request = (
        Select(Extracted_Result)
        .where(
            Extracted_Result.processing_request_id
            == processing_request_id
        )
    )
    result = await db_session.execute(request)
    response = result.scalar_one_or_none()
    return response


async def get_document_by_id(id: int, db_session: AsyncSession) -> Document | None:
    statement = Select(Document).where(Document.id == id)
    result = await db_session.execute(statement)
    response = result.scalar_one_or_none()
    return response


async def get_all_documents(page: int, limit:int, db_session: AsyncSession):
    offset = (page - 1) * limit
    statement = Select(Document).offset(offset).limit(limit)
    result =  await db_session.execute(statement)
    response = result.scalars().all()
    return response

async def get_total_no_of_documents(db_session: AsyncSession):
    statement = Select(func.count(Document.id))
    result = await db_session.execute(statement)
    response = result.scalar_one()
    return response


async def delete_document_by_id(id: int, db_session: AsyncSession):
    try:
        document = await get_document_by_id(id=id, db_session=db_session)
        if document:
            await db_session.delete(document)
            await db_session.commit()
    except:
        await db_session.rollback()


async def get_file_id(id: int, db_session: AsyncSession):
    stmt = Select(File).where(File.id == id)

    file_record = await db_session.execute(stmt)

    result = file_record.scalar_one_or_none()

    return result

async def get_jobs(id: int, db_session: AsyncSession) -> list[Processing_Job]:
    stmt = Select(Processing_Job).where(Processing_Job.processing_request_id == id)
    processing_job_record = await db_session.execute(stmt)
    result = processing_job_record.scalars().all()
    return list(result)

async def get_processing_request_by_id(id: int, db_session: AsyncSession):
    stmt = Select(Processing_Request).where(Processing_Request.id == id)
    record = await  db_session.execute(stmt)
    result = record.scalar_one_or_none();
    return result