from typing import Optional

from pymongo.errors import BulkWriteError
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult, BulkWriteResult
from pymongo.operations import UpdateOne

from src.config.database import db
from src.aggregation_queries.search_terms.search_terms_list import get_search_terms_list_pipeline
from src.logger import logger


class SearchTermsRepository:
    """
    Responsible for CRUD operations on search terms.
    Also, responsible for complex operations on search terms such as aggregation.
    """

    async def get_search_terms_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                                    skip: int = 0,
                                    limit: int = 0,
                                    **kwargs) -> list:
        """
        Returns a list of search_terms matching the given filters.
        :param filters: A query that matches documents.
        :param projection: A dictionary with fields that must be included in the result
        :param skip: The number of search_terms to skip
        :param limit: The number of search_terms to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if filters is None:
            filters = {}

        if projection is None:
            projection = {}

        search_terms = await db.search_terms \
            .find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return search_terms

    async def get_search_terms_with_document_count(self, page: int, page_size: int):
        """
            Returns specified number of search terms and total search term count,
            :param page_size - number of search terms to return
            :param page - page number.
        """
        pipeline = get_search_terms_list_pipeline(page, page_size)
        search_terms = await db.search_terms.aggregate(pipeline).to_list(length=None)
        return search_terms[0] if search_terms else {}

    async def get_one_search_term(self, filters: dict, projection: Optional[dict] = None, **kwargs) -> dict:
        """
        Returns one search terms based on filter conditions
        :param filters: A query that matches the document.
        :param projection: A dictionary with fields that must be included in the result
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if projection is None:
            projection = {}

        search_term = await db.search_terms.find_one(filters, projection, **kwargs)
        return search_term

    async def create_search_term(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Creates a new search term
        :param kwargs: Other parameters for insert such as session for transaction etc.
        :param data: search term data.
        """
        if not data:
            raise ValueError("No data provided")

        created_search_term = await db.search_terms.insert_one(data, **kwargs)
        return created_search_term

    async def update_search_term(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
        Updates a search term
        :param filters: A query that matches the document to update.
        :param data_to_update: Changed search term data and operations on them ($set and so on).
        :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_search_term = await db.search_terms.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_search_term

    async def delete_search_term(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes a search term
        :param filters: A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_search_term = await db.search_terms.delete_one(filter=filters, **kwargs)
        return deleted_search_term

    async def delete_many_search_terms(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes many search terms.
        :param filters: A query that matches the documents to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_many_search_terms = await db.search_terms.delete_many(filter=filters, **kwargs)
        return deleted_many_search_terms

    async def update_many_search_terms_bulk(self, operations: list[UpdateOne], **kwargs) -> BulkWriteResult:
        """
        Use this method when you want to set the different data to different search_terms.
        Performs bulk update of search_terms.
        :param operations: list of UpdateOne operations.
        :param kwargs: Other parameters for bulk write such as order of operations and so on.
        """
        try:
            updated_search_terms = await db.search_terms.bulk_write(operations, **kwargs)
            return updated_search_terms
        except BulkWriteError as bwe:
            logger.error(bwe)
