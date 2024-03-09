from typing import Dict, List
from datetime import datetime
from math import ceil
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.operations import UpdateOne

from .repository import SearchTermsRepository
from .schemes.base import SearchTermBase
from .schemes.update import UpdateSearchTerm
from .schemes.create import CreateSearchTerm


class SearchTermsAdminService:
    def __init__(self, search_repository: SearchTermsRepository):
        self.search_repository = search_repository

    async def search_terms_list(self, page: int, page_size: int, name: str) -> Dict:
        search_terms = await self.search_repository.get_search_terms_with_document_count(page, page_size, name)
        if not search_terms.get("result"):
            result = {
                "result": [],
                "page_count": 1,
            }
            return result

        search_terms_count = search_terms.get("total_count").get("total")

        result = {
            "result": search_terms.get("result"),
            "page_count": ceil(search_terms_count / page_size),  # Calculating count of pages
        }

        return result

    async def get_search_term_by_id(self, search_term_id: ObjectId) -> Dict:
        # Retrieve a search term with the specified ID
        search_term = await self.search_repository.get_one_search_term({"_id": search_term_id})
        if not search_term:
            raise HTTPException(status_code=404, detail="Search term not found")
        # Otherwise return search term
        return search_term

    async def create_search_term(self, data_to_insert: CreateSearchTerm) -> ObjectId:
        existed_search_term = await self.search_repository.get_one_search_term({"name": data_to_insert.name})
        if existed_search_term:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"name": "This search term already exists"})

        data_to_insert = SearchTermBase.parse_obj(
            {**data_to_insert.dict(), "search_count": 0, "last_searched": datetime.utcnow()})

        created_search_term = await self.search_repository.create_search_term(data=data_to_insert.dict())
        return created_search_term.inserted_id

    async def update_search_term(self, search_term_id: ObjectId,
                                 data_to_update: UpdateSearchTerm) -> int:
        # Retrieve a search term with the specified ID
        search_term = await self.search_repository.get_one_search_term({"_id": search_term_id},
                                                                       {"_id": 1})
        if not search_term:
            raise HTTPException(status_code=404, detail="Search term not found")

        existed_search_term = await self.search_repository.get_one_search_term(
            {"_id": {"$ne": search_term_id}, "name": data_to_update.name}, {"_id": 1})

        if existed_search_term:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"name": "This search term already exists"})

        updated_search_terms = await self.search_repository.update_search_term(
            {"_id": search_term_id},
            {"$set": data_to_update.dict()})

        return updated_search_terms.modified_count

    async def delete_search_term(self, search_term_id: ObjectId) -> int:
        deleted_search_term = await self.search_repository.delete_search_term({"_id": search_term_id})
        return deleted_search_term.deleted_count

    async def delete_many_search_terms(self, search_term_ids: List[ObjectId]) -> int:
        deleted_search_terms = await self.search_repository.delete_many_search_terms({"_id": {"$in": search_term_ids}})
        return deleted_search_terms.deleted_count

    async def create_search_terms_if_not_exist(self, search_terms: List[str], session=None):
        """
        Create new search terms from the input list if they do not exist
        """
        operations = []
        for search_term in search_terms:
            operation = UpdateOne(filter={"name": search_term},
                                  update={"$setOnInsert": {"search_count": 0, "last_searched": datetime.utcnow()}},
                                  upsert=True)
            operations.append(operation)

        if operations:
            await self.search_repository.update_many_search_terms_bulk(operations=operations, session=session)


    async def reset_search_count(self):
        await self.search_repository.update_many_search_terms({}, {"$set": {"search_count": 0}})