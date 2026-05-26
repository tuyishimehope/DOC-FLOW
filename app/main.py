from fastapi import FastAPI
from app.api.v1.document.document import router

app = FastAPI()

app.include_router(router=router)

@app.get("/")
def ready():
    return "APP IS RUNNING"

@app.get("/health")
def health():
    return "APP IS RUNNING"
