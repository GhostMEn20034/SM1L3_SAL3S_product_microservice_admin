from typing import List
from bson import ObjectId
from pydantic import BaseModel

from .base import CreatedSynonym


class SynonymListResponse(BaseModel):
    synonyms: List[CreatedSynonym]
    page_count: int

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class SynonymDetailResponse(BaseModel):
    synonym: CreatedSynonym
    # Data essential for synonym creation
    creation_essentials: dict

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}
