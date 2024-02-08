from typing import Optional
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from src.database import db


class SynonymRepository:
    """
    Responsible for CRUD operations on synonyms.
    Also, responsible for complex operations on synonyms such as aggregation.
    """

    async def get_synonym_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                               skip: int = 0,
                               limit: int = 0,
                               **kwargs) -> list:
        """
        Returns a list of synonyms.
        Params:
        :param filters: - A query that matches documents.
        :param projection: - Dictionary with fields must be included in the result
        :param skip: - Number of synonyms to skip
        :param limit: - Number of synonyms to return
        :param kwargs: Other parameters such as session for transaction etc.
        """
        # # If filters is not specified, then set filters to empty dict
        if filters is None:
            filters = {}
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        synonyms = await db.synonyms.find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)
        return synonyms

    async def get_synonym_list_with_documents_count(self, page: int, page_size: int, filters: dict = None) -> dict:
        """
            Returns specified number of synonyms and total synonym count,
            :param filters - dict with parameters used to filter synonyms
            :param page - page number
            :param page_size - number of synonyms to return
        """
        if not filters:
            filters = {}

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
        synonyms = await db.synonyms.aggregate(pipeline).to_list(length=None)
        return synonyms[0] if synonyms else {}

    async def get_one_synonym(self, filters: dict, projection: Optional[dict] = None, **kwargs) -> dict:
        """
        Find specific synonym by the given filter
        Params:
        :param filters: - A query that matches the document.
        :param projection: - Dictionary with fields must be included in the result
        :param kwargs: Other parameters such as session for transaction etc.
        """
        if projection is None:
            projection = {}

        synonym = await db.synonyms.find_one(filters, projection, **kwargs)
        return synonym

    async def create_synonym(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Create a new synonym.
        Params:
        :param data: Dictionary with synonym data
        :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_synonym = await db.synonyms.insert_one(data, **kwargs)
        return created_synonym

    async def update_synonym(self, filters: dict, data_to_update: dict, **kwargs) -> UpdateResult:
        """
            Updates synonym with specified filters,
            :param filters - A query that matches the document to update
            :param data_to_update - new synonym properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_synonym = await db.synonyms.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_synonym

    async def delete_one_synonym(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes synonym with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_synonym = await db.synonyms.delete_one(filter=filters, **kwargs)
        return deleted_synonym

    async def delete_many_synonyms(self, filters: dict, **kwargs):
        """
        Deletes many synonyms with specified filters
        :param filters: - A query that matches documents to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_synonyms = await db.synonyms.delete_many(filter=filters, **kwargs)
        return deleted_synonyms
