from celery import Celery

from app.core.config import settings

celery_app = Celery('docflow', broker=settings.broker_host,
             backend=settings.broker_backend)

celery_app.autodiscover_tasks(
    ["app.tasks"]
)