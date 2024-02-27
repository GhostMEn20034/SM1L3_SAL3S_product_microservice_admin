from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from typing import Optional

from src.config.database import db
from src.aggregation_queries.categories.category_list import get_category_list_pipeline


class CategoryRepository:
    """
        Responsible for CRUD operations on categories.
        Also, responsible for complex operations on categories such as aggregation.
    """

    async def get_category_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                                skip: int = 0,
                                limit: int = 0,
                                **kwargs) -> list:
        """
        Returns a list of categories matching the given filters.
        :param filters: A query that matches documents.
        :param projection: A dictionary with fields that must be included in the result
        :param skip: The number of categories to skip
        :param limit: The number of categories to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if filters is None:
            filters = {}

        if projection is None:
            projection = {}

        categories = await db.categories \
            .find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return categories

    async def get_categories_with_document_count(self, page: int, page_size: int):
        """
            Returns specified number of categories and total category count,
            :param page_size - number of categories to return
            :param page - page number.
        """
        pipeline = get_category_list_pipeline(page, page_size)
        categories = await db.categories.aggregate(pipeline).to_list(length=None)
        return categories[0] if categories else {}

    async def get_one_category(self, filters: dict, projection: Optional[dict] = None, **kwargs) -> dict:
        """
        Returns one category based on filter conditions
        :param filters: A query that matches the document.
        :param projection: A dictionary with fields that must be included in the result
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if projection is None:
            projection = {}

        category = await db.categories.find_one(filters, projection, **kwargs)
        return category

    async def create_category(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Creates a new category
        :param kwargs: Other parameters for insert such as session for transaction etc.
        :param data: Category data.
        """
        if not data:
            raise ValueError("No data provided")

        created_category = await db.categories.insert_one(data, **kwargs)
        return created_category

    async def update_category(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
        Updates a category
        :param filters: A query that matches the document to update.
        :param data_to_update: Changed category data and operations on them ($set and so on).
        :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_category = await db.categories.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_category

    async def delete_category(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes a category
        :param filters: A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_category = await db.categories.delete_one(filter=filters, **kwargs)
        return deleted_category
