import os
from celery import Celery
from celery.utils.log import get_task_logger
from src.services.fixed_periodic_tasks import initialize_fixed_periodic_tasks

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

celery.autodiscover_tasks(["src.services.events", "src.services.search_terms"])

logger = get_task_logger(__name__)

@celery.task(name="print_hello_world")
def print_hello_world():
    logger.info("Hello World!")

initialize_fixed_periodic_tasks()
