from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from typing import Optional

from src.config.database import db
from src.aggregation_queries.variation_themes.variation_theme_list import get_variation_theme_list_pipeline

class VariationThemeRepository:
    """
        Responsible for CRUD operations on variation themes.
        Also, responsible for complex operations on variation themes such as aggregation.
    """
    async def get_variation_theme_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                              skip: int = 0,
                              limit: int = 0,
                              **kwargs) -> list:
        """
        Returns a list of variation themes.
        Params:
        :param filters: - A query that matches documents.
        :param projection: - Dictionary with fields must be included in the result
        :param skip: - Number of variation themes to skip
        :param limit: - Number of variation themes to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        # If filters is not specified, then set filters to empty dict
        if filters is None:
            filters = {}
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        variation_themes = await db.variation_themes \
            .find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return variation_themes

    async def get_variation_themes_with_doc_count(self, page: int, page_size: int):
        """
        Returns a list of variation themes with document count
        :param page: Number of page.
        :param page_size: Number of documents per page.
        """
        pipeline = get_variation_theme_list_pipeline(page, page_size)
        variation_themes = await db.variation_themes.aggregate(pipeline).to_list(length=None)

        return variation_themes[0] if variation_themes else {}

    async def get_one_variation_theme(self, filters: dict, projection: Optional[dict] = None, **kwargs):
        """
           Find a specific variation_theme by the given filter
           Params:
           :param filters: - A query that matches the document.
           :param projection: - Dictionary with fields must be included in the result
           :param kwargs: Other parameters such as session for transaction etc.
        """
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        variation_theme = await db.variation_themes.find_one(filters, projection, **kwargs)

        return variation_theme

    async def create_variation_theme(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Create a new variation theme.
        Params:
        :param data: Dictionary with variation theme data
        :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_facet = await db.variation_themes.insert_one(data, **kwargs)

        return created_facet

    async def update_variation_theme(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
            Updates variation theme with specified filters,
            :param filters - A query that matches the document to update
            :param data_to_update - new variation_theme properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_variation_theme = await db.variation_themes.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_variation_theme

    async def delete_variation_theme(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes variation theme with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_variation_theme = await db.variation_themes.delete_one(filter=filters, **kwargs)
        return deleted_variation_theme
