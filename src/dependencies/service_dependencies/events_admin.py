from src.apps.events_admin.service import EventAdminService
from .products_admin import get_product_admin_service
from src.apps.events_admin.repository import EventRepository


async def get_event_admin_service() -> EventAdminService:
    repository = EventRepository()
    product_service = await get_product_admin_service()
    return EventAdminService(repository, product_service)