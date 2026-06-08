import os
from fastapi import FastAPI
from app.api.v1.document.document import router
from app.db.engine import engine
from app.core.minio import minio_client


def startup():
    print("Checking DB connection...")
    with engine.connect() as conn:
        print("Database Connected!")

    bucket_name = os.getenv("MINIO_BUCKET", "")

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket created: {bucket_name}")
    else:
        print("Bucket exists!")

    print("Existing buckets:")
    for bucket in minio_client.list_buckets():
        print(bucket.name, bucket.creation_date)

app = FastAPI(lifespan=startup())

app.include_router(router=router)



@app.get("/")
def ready():
    return "APP IS RUNNING"

@app.get("/health")
def health():
    return "APP IS RUNNING"
