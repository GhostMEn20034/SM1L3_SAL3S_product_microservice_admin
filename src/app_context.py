def get_celery_app():
    from src.worker import celery
    return celery