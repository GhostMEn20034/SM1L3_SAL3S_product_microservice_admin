from typing import Union, List, Tuple, Dict, Optional
from src.app_context import get_celery_app

from redbeat import RedBeatSchedulerEntry
from redbeat.schedules import rrule
from src.celery_logger import logger

def create_periodic_task(name: str, func, interval: rrule,
                         args: Optional[Union[List, Tuple]] = None,
                         kwargs: Optional[Dict] = None,
                         celery_app=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    if celery_app is None:
        celery_app = get_celery_app()

    entry = RedBeatSchedulerEntry(name, func, interval, args=args, kwargs=kwargs, app=celery_app)
    entry.save()
    logger.info(f"Created periodic task {name}")


def delete_periodic_task(name: str, celery_app=None):
    if celery_app is None:
        celery_app = get_celery_app()

    try:
        entry = RedBeatSchedulerEntry.from_key("redbeat:" + name, app=celery_app)
    except KeyError:
        entry = None

    if entry:
        entry.delete()
        logger.info(f"Deleted periodic task {name}")
