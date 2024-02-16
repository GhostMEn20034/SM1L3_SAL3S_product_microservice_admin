from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import Optional, List, Union

from src.schemes.py_object_id import PyObjectId
from .base import Deal, ParentDeal


class DealListElement(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)
    is_parent: bool
    parent_name: Optional[constr(min_length=1)]


class DealListResponse(BaseModel):
    result: List[DealListElement]
    page_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class CategoryElement(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)


class ParentDealElement(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)

class FacetElement(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)
    code: constr(min_length=1)
    type: constr(min_length=1)
    optional: bool
    units: Optional[List[constr(min_length=1)]]
    values: Optional[List[constr(min_length=1)]]


class DealCreationEssentialsResponse(BaseModel):
    categories: List[CategoryElement]
    parent_deals: List[ParentDealElement]
    facets: List[FacetElement]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class DealDetailResponse(BaseModel):
    deal: Union[Deal, ParentDeal]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}
