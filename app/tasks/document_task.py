import asyncio
from datetime import datetime

from sqlalchemy import Select

from app.service.document.schema import Processing_Job_Status, Processing_Type, Processing_status
from app.service.file.file import get_file
from app.service.openai.service import OpenaiService
from app.utils.document import extract_text_from_doc, extract_text_from_pdf
from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal, SyncSession
from app.models.schema import Document, Extracted_Result, File, Processing_Job, Processing_Request


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def start_processing(self, processing_request_id: int):
    try:
        asyncio.run(process_document(
            self=self,
            processing_request_id=processing_request_id
        ))
    except Exception as e:
        print("An unexpected error occurred", e)


async def process_document(self, processing_request_id: int):

    db_session = SyncSession()
    processing_request_result = None
    job = None
    try:
        processing_request_statement = db_session.execute(Select(Processing_Request).where(Processing_Request.id == processing_request_id
                                                                                           ))
        processing_request_result = processing_request_statement.scalar_one_or_none()

        if processing_request_result is None:
            return

        document_statement = db_session.execute(Select(Document).where(
            Document.id == processing_request_result.document_id
        ))
        document_statement_result = document_statement.scalar_one_or_none()

        if document_statement_result is None:
            return

        file_statement = db_session.execute(Select(File).where(
            File.id == document_statement_result.file_id))
        file_statement_result = file_statement.scalar()

        if file_statement_result is None:
            return

        file_object = get_file(file_id=file_statement_result.id)

        processing_type = processing_request_result.processing_type
        instructions = processing_request_result.instructions

        extracted_content = ""
        if file_statement_result.content_type == "application/pdf":
            extracted_content = extract_text_from_pdf(
                file_stream=file_object)
        elif file_statement_result.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_content = extract_text_from_doc(
                file_stream=file_object)

        if not extracted_content:
            return

        processing_request_result.status = (
            Processing_status.PROCESSING
        )

        db_session.commit()

        job = Processing_Job(
            processing_request_id=processing_request_result.id,
            attempt_number=self.request.retries + 1,
            status=Processing_Job_Status.RUNNING,
            started_at=datetime.now()
        )

        db_session.add(job)
        db_session.commit()

        if processing_type == Processing_Type.DOCUMENT_SUMMARY:
            result = await OpenaiService().generate_summary(
                content=extracted_content, instructions=instructions)
        elif processing_type == Processing_Type.INVOICE_EXTRACTION:
            result = await OpenaiService().get_invoice_metadata(
                content=extracted_content, instructions=instructions)
        elif processing_type == Processing_Type.CONTRACT_METADATA:
            result = await OpenaiService().get_contract_metadata(
                content=extracted_content, instructions=instructions)
        else:
            return

        if result:
            processing_request_result.status = Processing_status.COMPLETED
            db_session.add(processing_request_result)
            db_session.commit()

            extracted_result_object = Extracted_Result(processing_request_id=processing_request_result.id,
                                                       result_type=processing_type.value, content_json={'result': result}, confidence_score=1.0)

            job.status = Processing_Job_Status.COMPLETED
            job.completed_at = datetime.now()

            db_session.add_all([extracted_result_object, job
                                ])
            db_session.commit()

    except Exception as e:
        if processing_request_result:
            processing_request_result.status = Processing_status.FAILED

        if job:
            job.status = Processing_Job_Status.FAILED
            job.completed_at = datetime.now()

        db_session.commit()

        raise
    finally:
        db_session.close()
