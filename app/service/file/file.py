import os

from fastapi import UploadFile
import datetime

from app.core.minio import minio_client
from app.service.auth.auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.file.crud import get_file_id

BUCKET_NAME = os.getenv("MINIO_BUCKET", "")


async def post_file(file: UploadFile, file_id: str):

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=file_id,
        data=file.file,
        length=size,
        content_type=file.content_type or "",
    )

    return {
        "file_id": file_id
    }


def get_file(file_id: int):
    return minio_client.get_object(BUCKET_NAME, str(file_id))


def delete_file(file_id: int):
    minio_client.remove_object(BUCKET_NAME, str(file_id))


async def update_file(file: UploadFile, file_id: int):
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=str(file_id),
        data=file.file,
        length=size,
        content_type=file.content_type or "",
    )

    return {"updated": file_id}


async def get_file_by_id(id: int, current_user: CurrentUser, db_session: AsyncSession):

    file_record = await get_file_id(id=id, current_user=current_user, db_session=db_session)

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


async def delete_file_by_id(id: int, current_user: CurrentUser, db_session: AsyncSession):
    file_record = await get_file_id(id=id, current_user=current_user, db_session=db_session)

    if not file_record:
        return None
    
    file_record.deleted_at = datetime.datetime.now()

    await db_session.commit()
    
    return id
    
