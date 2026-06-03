from fastapi import FastAPI
from app.api.v1.document.document import router
from app.db.engine import engine

app = FastAPI()

app.include_router(router=router)

@app.get("/")
def ready():
    with engine.connect() as conn:
        print("Connected!")
        
    return "APP IS RUNNING"

@app.get("/health")
def health():
    return "APP IS RUNNING"
