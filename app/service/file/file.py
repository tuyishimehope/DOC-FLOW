import os
import uuid
from fastapi import UploadFile
from app.core.minio import minio_client

BUCKET_NAME = os.getenv("MINIO_BUCKET", "docflow-bucket")


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