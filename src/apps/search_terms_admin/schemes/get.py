from typing import List
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
