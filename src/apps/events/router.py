import fastapi

from src.apps.events.schemes.get import EventListResponse, EventsDetailResponse
from .schemes.create import CreateEvent
from .schemes.update import UpdateEvent
from .service import EventAdminService
from src.dependencies.service_dependencies.events import get_event_service
from src.schemes.py_object_id import PyObjectId

router = fastapi.APIRouter(
    prefix='/admin/events',
    tags=["Events"],
)


@router.get('/', response_model=EventListResponse)
async def get_event_list(page: int = fastapi.Query(1, ge=1, ),
                         page_size: int = fastapi.Query(15, ge=0),
                         service: EventAdminService = fastapi.Depends(get_event_service)):
    return await service.get_event_list(page, page_size)


@router.get('/{event_id}', response_model=EventsDetailResponse)
async def get_event_details(event_id: PyObjectId,
                            service: EventAdminService = fastapi.Depends(get_event_service)):
    return await service.get_event_by_id(event_id)


@router.post('/')
async def create_event(event_data: CreateEvent,
                       service: EventAdminService = fastapi.Depends(get_event_service)):
    await service.create_event(event_data)


@router.put('/{event_id}', status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def update_event(event_id: PyObjectId, event_data: UpdateEvent = fastapi.Body(...),
                       service: EventAdminService = fastapi.Depends(get_event_service)):
    await service.update_event(event_id, event_data)


@router.delete('/{event_id}', status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: PyObjectId,
                       service: EventAdminService = fastapi.Depends(get_event_service)):
    await service.delete_event(event_id)
