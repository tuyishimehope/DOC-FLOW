from minio import Minio
import os

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", ""),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
)