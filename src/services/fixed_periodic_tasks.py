from redbeat.schedules import rrule
from .celery_beats_operations import create_periodic_task

def initialize_fixed_periodic_tasks():
    reset_search_count_interval = rrule(freq="WEEKLY", interval=2)
    create_periodic_task('task_reset_search_count', 'reset_search_count', reset_search_count_interval, )