from celery import Celery

import os 

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery('docflow', broker=os.getenv("broker_host"),
             backend=os.getenv("broker_backend"))

celery_app.autodiscover_tasks(
    ["app.tasks"]
)