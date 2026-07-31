from fastapi import FastAPI
from fastapi.testclient import TestClient


demo_app = FastAPI()

@demo_app.get("/")
def message():
    return {"message": "Hello world"}

client = TestClient(demo_app)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200