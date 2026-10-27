from celery import Celery

from app.core.config import get_settings

celery_app = Celery("todo", broker=get_settings().celery_broker_url, include=["app.worker.tasks"])
celery_app.conf.update(
    task_acks_late=True, task_serializer="json", accept_content=["json"], timezone="UTC"
)
