from pydantic import BaseModel, Field
from typing import List, Any, Optional, Union
from src.schemes import PyObjectId
from bson import ObjectId
import fastapi


class Facet(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: str
    name: str
    type: str
    values: Optional[List[Any]]
    categories: Optional[Union[List[Any], str]]
    optional: Optional[bool]
    show_in_filters: Optional[bool]


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class FacetFilters(BaseModel):
    categories: Optional[List[PyObjectId]] = Field(fastapi.Query([]))
    type: Optional[List[str]] = Field(fastapi.Query([]))
    optional: bool = None
    show_in_filters: bool = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class FacetList(BaseModel):
    result: List[Facet]
    page_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class FacetUpdate(BaseModel):
    name: str
    optional: bool
    show_in_filters: bool
    categories: List[PyObjectId]
    values: Optional[List[Any]]

    class Config:
        json_encoders = {ObjectId: str}
