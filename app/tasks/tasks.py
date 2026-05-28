import os 

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery('tasks', broker=os.getenv("broker_host"),
             backend=os.getenv("broker_host"))


@app.task
def add(x, y):
    print(1)
    return x + y
