from math import ceil
from typing import List
from bson import ObjectId
from fastapi import HTTPException

from .repository import SynonymRepository
from .schemes.base import MappingTypeEnum
from .schemes.create import SynonymCreate
from .schemes.update import SynonymUpdate


class SynonymService:
    def __init__(self, repository: SynonymRepository):
        self.repository = repository

    async def get_synonym_creation_essentials(self) -> dict:
        mapping_types = [i.value for i in MappingTypeEnum]
        return {"mappingTypes": mapping_types}

    async def create_synonym(self, data: SynonymCreate) -> None:
        mapping_type = data.mappingType
        data.synonyms = [synonym.strip() for synonym in data.synonyms]
        if mapping_type == MappingTypeEnum.explicit.value:
            data.input = [i.strip() for i in data.input]
            input_tokens = data.input
            synonyms = data.synonyms
            if not all(element in synonyms for element in input_tokens):
                raise HTTPException(status_code=400, detail={"input": "Input tokens must be contained in synonyms"})

        created_synonym = await self.repository.create_synonym(data.dict(exclude_none=True))
        if not created_synonym.inserted_id:
            raise HTTPException(status_code=400, detail="Synonym not created")

    async def get_synonym_list(self, page: int, page_size: int) -> dict:
        synonyms = await self.repository.get_synonym_list_with_documents_count(page, page_size)
        # If there are no results
        # then return default response
        if not synonyms.get("result"):
            result = {
                "synonyms": [],
                "page_count": 1,
            }
            return result

        synonyms_count = synonyms.get("total_count").get("total")

        result = {
            "synonyms": synonyms.get("result"),
            "page_count": ceil(synonyms_count / page_size),
        }
        # return result
        return result

    async def get_synonym_by_id(self, synonym_id: ObjectId) -> dict:
        synonym = await self.repository.get_one_synonym({"_id": synonym_id})
        # if there's no synonym with the specified id raise HTTP 404 Not Found
        if not synonym:
            raise HTTPException(status_code=404, detail="Synonym not found")
        # Otherwise return synonym with the given id
        return synonym

    async def update_synonym(self, synonym_id: ObjectId, data_to_update: SynonymUpdate) -> None:
        synonym = await self.repository.get_one_synonym({"_id": synonym_id},
                                                        {"_id": 1, "mappingType": 1})
        if not synonym:
            raise HTTPException(status_code=404, detail="Synonym not found")

        data_to_update.synonyms = [synonym.strip() for synonym in data_to_update.synonyms]
        if synonym["mappingType"] == MappingTypeEnum.explicit.value:
            data_to_update.input = [i.strip() for i in data_to_update.input]
            input_tokens = data_to_update.input
            synonyms = data_to_update.synonyms
            if not all(element in synonyms for element in input_tokens):
                raise HTTPException(status_code=400, detail={"input": "Input tokens must be contained in synonyms"})

        await self.repository.update_synonym({"_id": synonym_id},
                                             {"$set": data_to_update.dict(exclude_none=True)})

    async def delete_one_synonym(self, synonym_id: ObjectId) -> None:
        synonym = await self.repository.get_one_synonym({"_id": synonym_id}, {"_id": 1})
        if not synonym:
            raise HTTPException(status_code=404, detail="Synonym not found")

        await self.repository.delete_one_synonym({"_id": synonym_id})

    async def delete_many_synonyms(self, synonym_ids: List[ObjectId]) -> None:
        synonyms = await self.repository.get_synonym_list({"_id": {"$in": synonym_ids}}, {"_id": 1})
        if not synonyms:
            raise HTTPException(status_code=404, detail="Synonyms not found")

        await self.repository.delete_many_synonyms({"_id": {"$in": synonym_ids}})
