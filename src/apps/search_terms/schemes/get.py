from typing import List
import fastapi
from bson import ObjectId
from pydantic import BaseModel

from .base import SearchTerm


class SearchTermsListResponse(BaseModel):
    result: List[SearchTerm]
    page_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class SearchTermDetailResponse(BaseModel):
    search_term: SearchTerm

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class SearchTermsFilters(BaseModel):
    page: int = fastapi.Query(1, ge=1),
    page_size: int = fastapi.Query(40, ge=0)
    name: str = fastapi.Query('')
