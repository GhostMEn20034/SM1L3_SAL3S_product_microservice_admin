from typing import Optional
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from src.config.database import db
from src.aggregation_queries.events_admin.event_list import get_event_list_pipeline


class EventRepository:
    """
    Responsible for CRUD operations on events.
    Also, responsible for complex operations on events such as aggregation.
    """
    async def get_event_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                               skip: int = 0,
                               limit: int = 0,
                               **kwargs) -> list:
        """
        Returns a list of events.
        Params:
        :param filters: - A query that matches documents.
        :param projection: - Dictionary with fields must be included in the result
        :param skip: - Number of events to skip
        :param limit: - Number of events to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if filters is None:
            filters = {}

        if projection is None:
            projection = {}

        events = await db.events.find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(
            length=None)
        return events

    async def get_event_list_with_documents_count(self, page: int, page_size: int) -> dict:
        """
        Returns specified number of events and total events count,
        :param page - page number
        :param page_size - number of events to return
        """
        pipeline = get_event_list_pipeline(page, page_size)
        events = await db.events.aggregate(pipeline).to_list(length=None)
        return events[0] if events else {}

    async def get_one_event(self, filters: dict, projection: Optional[dict] = None, **kwargs) -> dict:
        """
        Find specific event by the given filter
        Params:
        :param filters: - A query that matches the document.
        :param projection: - Dictionary with fields must be included in the result
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if projection is None:
            projection = {}

        event = await db.events.find_one(filters, projection, **kwargs)
        return event

    async def create_event(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Create a new event.
        Params:
        :param data: Dictionary with event data
        :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_event = await db.events.insert_one(data, **kwargs)
        return created_event

    async def update_event(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
            Updates event with specified filters,
            :param filters - A query that matches the document to update
            :param data_to_update - new event properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_event = await db.events.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_event

    async def delete_one_event(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Delete event with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_event = await db.events.delete_one(filter=filters, **kwargs)
        return deleted_event

    async def delete_many_events(self, filters: dict, **kwargs):
        """
        Deletes many events with specified filters
        :param filters: - A query that matches documents to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_events = await db.events.delete_many(filter=filters, **kwargs)
        return deleted_events
