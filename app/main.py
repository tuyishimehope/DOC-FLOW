import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.document.document import router as document_router
from app.api.v1.file.file import router as file_router
from app.db.engine import engine
from app.core.minio import minio_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Checking DB connection...")

    async with engine.connect() as conn:
        print("Database Connected!")

    bucket_name = os.getenv("MINIO_BUCKET", "")

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    yield

app = FastAPI(lifespan=lifespan)


app.include_router(router=document_router)
app.include_router(router=file_router)



@app.get("/")
def ready():
    return "APP IS RUNNING"

@app.get("/health")
def health():
    return "APP IS RUNNING"
