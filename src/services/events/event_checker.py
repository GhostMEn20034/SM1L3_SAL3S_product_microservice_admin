from bson import ObjectId
from datetime import datetime
import pytz

from src.apps.events.repository import EventRepository
from src.apps.products.service import ProductAdminService
from src.apps.events.schemes.base import EventStatusEnum
from src.services.celery_beats_operations import delete_periodic_task
from src.worker import logger


class EventChecker:
    def __init__(self,product_service: ProductAdminService, event_repository: EventRepository):
        self.event_repository = event_repository
        self.product_service = product_service

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
                await self.event_repository.update_event({"_id": event_id},
                                            {"$set": {"status": EventStatusEnum.started.value}})
                updated_count = await self.product_service.set_product_discounts(
                    [product["_id"] for product in event["discounted_products"]],
                    [product["discount_rate"] for product in event["discounted_products"]],
                )
                logger.info(f"Event {event_id} started with {updated_count} discounts applied")
            else:
                logger.info(f"Too early to start event {event_id}")

        elif event["status"] == "started":
            # Check whether current date in utc is greater than end_date
            if current_date > end_date:
                await self.event_repository.update_event({"_id": event_id},
                                                         {"$set": {"status": EventStatusEnum.ended.value}})
                # Unset discounts
                updated_count = await self.product_service.set_product_discounts(
                    [product["_id"] for product in event["discounted_products"]],
                    None,
                )
                # Remove periodic task from the list of tasks
                delete_periodic_task(f"event_{str(event_id)}")

                logger.info(f"Event {event_id} ended and {updated_count} discounts were unset")
            else:
                logger.info(f"Too early to end event {event_id}")
