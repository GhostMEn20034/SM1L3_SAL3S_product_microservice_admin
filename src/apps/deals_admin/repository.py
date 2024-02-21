from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from typing import Optional

from src.config.database import db
from src.aggregation_queries.deals_admin.deal_list import get_deal_list_pipeline


class DealRepository:
    """
    Responsible for CRUD operations on deals.
    Also, responsible for complex operations on deals such as aggregation.
    """
    async def get_deal_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                              skip: int = 0,
                              limit: int = 0,
                              **kwargs) -> list:
        """
        Returns a list of deals.
        Params:
        :param filters: - A query that matches documents.
        :param projection: - Dictionary with fields must be included in the result
        :param skip: - Number of deals to skip
        :param limit: - Number of deals to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        # # If filters is not specified, then set filters to empty dict
        if filters is None:
            filters = {}
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        deals = await db.deals.find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return deals

    async def get_deal_list_with_deals_count(self, page: int, page_size: int, filters: Optional[dict] = None) -> dict:
        """
            Returns specified number of deals and total deal count,
            :param filters - dict with parameters used to filter deals
            :param page - page number
            :param page_size - number of deals to return
        """
        if filters is None:
            filters = {}

        pipeline = get_deal_list_pipeline(filters, page, page_size)
        deals = await db.deals.aggregate(pipeline).to_list(length=None)
        return deals[0] if deals else {}

    async def get_one_deal(self, filters: dict, projection: Optional[dict] = None, **kwargs) -> dict:
        """
        Find specific deal by the given filter
        Params:
        :param filters: - A query that matches the document.
        :param projection: - Dictionary with fields must be included in the result
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if projection is None:
            projection = {}

        deal = await db.deals.find_one(filters, projection, **kwargs)

        return deal

    async def create_deal(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Create a new deal.
        Params:
        :param data: Dictionary with deals data
        :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_deal = await db.deals.insert_one(data, **kwargs)

        return created_deal

    async def update_deal(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
            Updates deal with specified filters,
            :param filters - A query that matches the document to update
            :param data_to_update - new deal properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_deal = await db.deals.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_deal

    async def delete_deal(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes deals with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_deal = await db.deals.delete_one(filter=filters, **kwargs)
        return deleted_deal
