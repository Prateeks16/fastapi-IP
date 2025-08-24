from celery import Celery
from core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(
    "app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
celery.conf.task_routes = {
    "services.tasks.*": {"queue": "default"},
}
