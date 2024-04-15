from typing import Optional, List, Any, Union
import fastapi
from bson import ObjectId
from pydantic import BaseModel, Field

from src.schemes.py_object_id import PyObjectId
from .base import FacetBase, RangeValue


class Facet(FacetBase):
    """Detail facet representation"""
    values: Optional[List[Any]]
    categories: Union[List[PyObjectId], str]
    explanation: Optional[str]
    units: Optional[List[str]]
    is_range: bool = False
    range_values: Optional[List[RangeValue]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class FacetFilters(BaseModel):
    """Fields by which facet can be filtered"""
    categories: Optional[List[PyObjectId]] = Field(fastapi.Query([]))
    type: Optional[List[str]] = Field(fastapi.Query([]))
    optional: bool = None
    show_in_filters: bool = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class FacetList(BaseModel):
    """Model represents list of facets and shows page count"""
    result: List[FacetBase]
    page_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}