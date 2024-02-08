from celery import shared_task
from src.worker import logger


@shared_task
def some_task(number):
    logger.info(f"Result: {number * 10}")
    return number * 10
