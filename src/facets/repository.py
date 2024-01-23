from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from typing import Optional

from src.database import db


class FacetRepository:
    """
    Responsible for CRUD operations on facets.
    Also, responsible for complex operations on facets such as aggregation.
    """
    async def get_facet_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                              skip: int = 0,
                              limit: int = 0,
                              **kwargs) -> list:
        """
        Returns a list of facets.
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

        facets = await db.facets.find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return facets

    async def get_facet_list_with_facets_count(self, filters: dict, page: int, page_size: int) -> dict:
        """
            Returns specified number of facets and total facet count,
            :param filters - dict with parameters used to filter facets
            :param page - page number
            :param page_size - number of facets to return
        """
        pipeline = [
            {
                "$match": {
                    **filters
                }
            },
            {
                "$facet": {
                    "result": [
                        {
                            "$project": {
                                "values": 0,
                                "categories": 0
                            }
                        },
                        {
                            "$skip": (page - 1) * page_size
                        },
                        {
                            "$limit": page_size
                        }
                    ],
                    "total_count": [
                        {"$count": "total"}
                    ]
                },
            },
            {
                "$unwind": "$total_count",
            },
        ]

        facets = await db.facets.aggregate(pipeline).to_list(length=None)
        return facets[0] if facets else {}

    async def get_one_facet(self, filters: dict, projection: Optional[dict] = None, **kwargs) -> dict:
        """
        Find specific facet by the given filter
        Params:
        :param filters: - A query that matches the document.
        :param projection: - Dictionary with fields must be included in the result
        :param kwargs: Other parameters such as session for transaction etc.
        """
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        facet = await db.facets.find_one(filters, projection, **kwargs)

        return facet

    async def create_facet(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Create a new facet.
        Params:
        :param data: Dictionary with facet data
        :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_facet = await db.facets.insert_one(data, **kwargs)

        return created_facet

    async def update_facet(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
            Updates facet with specified filters,
            :param filters - A query that matches the document to update
            :param data_to_update - new facet properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_facet = await db.facets.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_facet

    async def delete_facet(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes facet with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_facet = await db.facets.delete_one(filter=filters, **kwargs)
        return deleted_facet
