from bson.objectid import ObjectId, InvalidId

from src.dependencies.service_dependencies.products_admin import get_product_admin_service
from src.apps.products_admin.service import ProductAdminService
from src.apps.events_admin.repository import EventRepository
from src.services.events_admin.event_checker import EventChecker
from src.worker import celery, logger
from src.utils import async_worker


@celery.task(name='check_event_task')
def check_event_task(event_id: str):

    logger.info(f"Ran periodic task event_{event_id}")

    try:
        converted_str_to_object_id = ObjectId(event_id)
    except InvalidId:
        return "Invalid ObjectId"

    product_service: ProductAdminService = async_worker(get_product_admin_service, )
    event_repository: EventRepository = EventRepository()
    event_checker = EventChecker(product_service, event_repository)
    async_worker(event_checker.check_event, converted_str_to_object_id)
