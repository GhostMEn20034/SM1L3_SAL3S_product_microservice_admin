from math import ceil
from bson import ObjectId
from fastapi import HTTPException
from redbeat.schedules import rrule

from .repository import EventRepository
from src.apps.products.service import ProductAdminService
from .schemes.create import CreateEvent
from .schemes.update import UpdateEvent
from src.services.events.event_validator import EventValidatorCreate, EventValidatorUpdate
from src.utils import convert_decimal, is_valid_url
from src.services.events.upload_event_images import upload_event_image
from src.services.events.delete_event_images import delete_event_image
from src.services.celery_beats_operations import create_periodic_task, delete_periodic_task
from src.config.settings import EVENT_CHECK_INTERVAL_MINUTES
from src.param_classes.products.detach_from_event_params import DetachFromEventParams


class EventAdminService:
    def __init__(self, repository: EventRepository, product_service: ProductAdminService):
        self.repository = repository
        self.product_service = product_service

    async def get_event_by_id(self, event_id: ObjectId) -> dict:
        event = await self.repository.get_one_event({"_id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return {"event": event}

    async def get_event_list(self, page: int, page_size: int) -> dict:

        events = await self.repository.get_event_list_with_documents_count(page, page_size)
        # If there are no results
        # then return default response
        if not events.get("result"):
            result = {
                "events": [],
                "page_count": 1,
            }
            return result

        events_count = events.get("total_count").get("total")

        result = {
            "events": events.get("result"),
            "page_count": ceil(events_count / page_size),
        }

        # return result
        return result

    async def create_event(self, data: CreateEvent):
        event_validator = EventValidatorCreate(data)
        errors = await event_validator.validate()
        if errors:
            raise HTTPException(status_code=400, detail=errors)
        data_to_insert = data.dict(by_alias=True)
        encoded_image: str = data_to_insert.pop("image")
        convert_decimal(data_to_insert)
        inserted_event = await self.repository.create_event(data_to_insert)
        # Upload event image to the storage
        # And add image link to the created event
        image_url = await upload_event_image(encoded_image, f"{inserted_event.inserted_id}_0.jpg")
        await self.repository.update_event({"_id": inserted_event.inserted_id},
                                           {"$set": {"image": image_url}})
        # create new event tracker
        interval = rrule(freq="MINUTELY", interval=EVENT_CHECK_INTERVAL_MINUTES)
        create_periodic_task(f"event_{str(inserted_event.inserted_id)}",
                             "check_event_task",
                             interval,
                             args=(str(inserted_event.inserted_id), ))

    async def update_event(self, event_id: ObjectId, data_to_update: UpdateEvent):
        event = await self.repository.get_one_event({"_id": event_id}, {"status": 1})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        event_validator = EventValidatorUpdate(data_to_update)
        errors = await event_validator.validate()
        if errors:
            raise HTTPException(status_code=400, detail=errors)

        # if there's an image value and it is not valid url
        if not is_valid_url(data_to_update.image) and data_to_update.image is not None:
            await upload_event_image(data_to_update.image,f"{event['_id']}_0.jpg")

        data_to_update = data_to_update.dict(by_alias=True, exclude_none=True)
        data_to_update.pop("image", None)

        # if an event already started or ended
        # you cannot change fields: start_date, end_date, discounted_products.
        # So these fields will be excluded from the data_to_update.
        if event["status"] != 'created':
            data_to_update.pop("start_date", None)
            data_to_update.pop("end_date", None)
            data_to_update.pop("discounted_products", None)

        convert_decimal(data_to_update)
        await self.repository.update_event({"_id": event_id}, {"$set": data_to_update})

    async def delete_event(self, event_id: ObjectId):
        event = await self.repository.get_one_event({"_id": event_id},
                                                    {"image": 1, "discounted_products": 1})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        await self.repository.delete_one_event({"_id": event_id})
        await delete_event_image(event["image"])
        detach_from_event_params = DetachFromEventParams(
            product_ids=[product["_id"] for product in event["discounted_products"]],
            event_id=event_id,
        )
        await self.product_service.detach_from_event(detach_from_event_params)
        delete_periodic_task(f"event_{str(event_id)}")