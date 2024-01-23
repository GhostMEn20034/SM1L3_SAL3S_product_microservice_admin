from typing import Optional
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from src.database import db


class FacetTypeRepository:
    """
        Responsible for CRUD operations on facet types.
    """
    async def get_facet_type_list(self, filters: Optional[dict] = None,
                                  projection: Optional[dict] = None,
                                  skip: int = 0, limit: int = 0, **kwargs) -> list:
        """
        Returns a list of facet types.
        Params:
        :param filters: - A query that matches documents.
        :param projection: - Dictionary with fields must be included in the result
        :param skip: - Number of facets to skip
        :param limit: - Number of facets to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        # # If filters is not specified, then set filters to empty dict
        if filters is None:
            filters = {}
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        facet_types = await db.facet_types \
                .find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return facet_types

    async def create_facet_type(self, data: dict, **kwargs) -> InsertOneResult:
        """
            Create a new facet type.
            Params:
            :param data: Dictionary with facet type data
            :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        inserted_facet_type = await db.facet_types.insert_one(document=data, **kwargs)
        return inserted_facet_type

    async def update_facet_type(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
            Updates facet with specified id,
            :param filters - A query that matches the document to update
            :param data_to_update - new facet properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_facet_type = await db.facet_types.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_facet_type

    async def delete_facet_type(self, filters: dict, **kwargs) -> DeleteResult:
        """
            Deletes facet type with the specified filters
            :param filters: - A query that matches the document to delete.
            :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_facet_type = await db.facet_types.delete_one(filter=filters, **kwargs)
        return deleted_facet_type
