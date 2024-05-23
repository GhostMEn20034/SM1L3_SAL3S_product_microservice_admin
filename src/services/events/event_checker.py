from bson import ObjectId
from datetime import datetime
import pytz

from src.apps.events.repository import EventRepository
from src.apps.products.service import ProductAdminService
from src.apps.events.schemes.base import EventStatusEnum
from src.param_classes.products.attach_to_event_params import AttachToEventParams
from src.param_classes.products.detach_from_event_params import DetachFromEventParams
from src.services.celery_beats_operations import delete_periodic_task
from src.celery_logger import logger


class EventChecker:
    def __init__(self,product_service: ProductAdminService, event_repository: EventRepository):
        self.event_repository = event_repository
        self.product_service = product_service

    async def _start_event(self, event: dict):
        await self.event_repository.update_event({"_id": event["_id"]},
                                                 {"$set": {"status": EventStatusEnum.started.value}})
        attach_to_event_params = AttachToEventParams(
            [product["_id"] for product in event["discounted_products"]],
            event["_id"],
            [product["discount_rate"] for product in event["discounted_products"]],
        )
        # Set discounts
        updated_count = await self.product_service.attach_to_event(attach_to_event_params)
        logger.info(f"Event {event['_id']} started with {updated_count} discounts applied")

    async def _end_event(self, event: dict):
        await self.event_repository.update_event({"_id": event["_id"]},
                                                 {"$set": {"status": EventStatusEnum.ended.value}})
        detach_from_event_params = DetachFromEventParams(
            event_id=event["_id"],
            product_ids=[product["_id"] for product in event["discounted_products"]],
        )
        # Unset discounts
        updated_count = await self.product_service.detach_from_event(detach_from_event_params)
        # Remove periodic task from the list of tasks
        delete_periodic_task(f"event_{str(event['_id'])}")
        logger.info(f"Event {event['_id']} ended and {updated_count} discounts were unset")

    async def check_event(self, event_id: ObjectId):
        # Get the event record from db
        event = await self.event_repository.get_one_event({"_id": event_id},
                                                              {"status": 1, "start_date": 1,
                                                                 "end_date": 1, "discounted_products": 1})
        utc = pytz.UTC # create a UTC timezone object
        # Get the current date in utc
        current_date = datetime.utcnow()
        current_date = utc.localize(current_date)
        logger.info(f"Current Date {current_date}")

        # Add timezone to the start and end dates
        start_date = pytz.utc.localize(event["start_date"])
        end_date = pytz.utc.localize(event["end_date"])

        if event["status"] == "created":
            # Check whether current date in utc is greater than start_date
            if current_date > start_date:
                # If it is , then start an event
                await self._start_event(event)
            else:
                logger.info(f"Too early to start event {event_id}")

        elif event["status"] == "started":
            # Check whether current date in utc is greater than end_date
            if current_date > end_date:
                # If it is , then end an event
                await self._end_event(event)
            else:
                logger.info(f"Too early to end event {event_id}")
