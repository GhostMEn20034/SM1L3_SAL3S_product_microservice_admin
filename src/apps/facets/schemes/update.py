from typing import Optional, List, Any, Union
from pydantic import BaseModel, constr, Field, validator
from bson import ObjectId

from src.schemes.py_object_id import PyObjectId
from .base import RangeValue



class FacetUpdate(BaseModel):
    """Model represents updatable facet fields"""
    name: constr(min_length=1) = Field(...)
    optional: bool
    show_in_filters: bool
    categories: Union[List[PyObjectId], str]
    explanation: Optional[str]
    units: Optional[List[str]]
    values: Optional[List[Any]]
    is_range: bool = False
    range_values: Optional[List[RangeValue]]

    @validator("categories")
    def categories_must_be_not_empty(cls, v):
        if not len(v) > 0 and not v == "*":
            raise ValueError("Categories must contain at least 1 item")
        return v

    @validator("values")
    def values_must_be_not_empty(cls, v, values):
        if v is not None and len(v) < 1:
            raise ValueError("Values must contain at least 1 item")

        return v

    @validator("range_values")
    def validate_range_values(cls, v, values):
        if not values["is_range"]:
            return None
        elif v is None and values["is_range"]:
            raise ValueError("Range values must not be None if the facet is range facet")

        return v

    class Config:
        json_encoders = {ObjectId: str}