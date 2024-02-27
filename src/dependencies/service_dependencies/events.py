from src.apps.events.service import EventAdminService
from .products import get_product_service
from src.apps.events.repository import EventRepository


async def get_event_service() -> EventAdminService:
    repository = EventRepository()
    product_service = await get_product_service()
    return EventAdminService(repository, product_service)