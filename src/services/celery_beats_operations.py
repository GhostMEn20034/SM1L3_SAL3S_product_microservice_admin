from typing import Union, List, Tuple, Dict, Optional
from celery import current_app

from redbeat import RedBeatSchedulerEntry
from redbeat.schedules import rrule
from src.worker import logger

def create_periodic_task(name: str, func, interval: rrule,
                         args: Optional[Union[List, Tuple]] = None,
                         kwargs: Optional[Dict] = None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    entry = RedBeatSchedulerEntry(name, func, interval, args=args, kwargs=kwargs, app=current_app)
    entry.save()
    logger.info(f"Created periodic task {name}")


def delete_periodic_task(name: str):
    try:
        entry = RedBeatSchedulerEntry.from_key("redbeat:" + name, app=current_app)
    except KeyError:
        entry = None

    if entry:
        entry.delete()
        logger.info(f"Deleted periodic task {name}")
