from pydantic import BaseModel, Field, constr, validator
from typing import List, Any, Optional, Union
from bson import ObjectId
import fastapi
from src.schemes.py_object_id import PyObjectId



class FacetBase(BaseModel):
    """
    Model that represents base facet fields
    used in the detail facet representation and in the list representation
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: str
    name: str
    type: str
    optional: bool
    show_in_filters: bool


class Facet(FacetBase):
    """Detail facet representation"""
    values: Optional[List[Any]]
    categories: Union[List[PyObjectId], str]
    explanation: Optional[str]
    units: Optional[List[str]]

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


class FacetUpdate(BaseModel):
    """Model represents updatable facet fields"""
    name: constr(min_length=1) = Field(...)
    optional: bool
    show_in_filters: bool
    categories: Union[List[PyObjectId], str]
    explanation: Optional[str]
    units: Optional[List[str]]
    values: Optional[List[Any]]

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

    class Config:
        json_encoders = {ObjectId: str}

class FacetCreate(BaseModel):
    """Model represents fields required to create a facet"""
    code: constr(min_length=1) = Field(...)
    name: constr(min_length=1) = Field(...)
    type: constr(min_length=1) = Field(...)
    values: Optional[List[Any]]
    categories: Union[List[PyObjectId], str]
    explanation: Optional[str]
    units: Optional[List[str]]
    optional: bool
    show_in_filters: bool

    @validator("categories")
    def categories_must_be_not_empty(cls, v):
        if not len(v) > 0 and not v == "*":
            raise ValueError("Categories must contain at least 1 item")
        return v

    @validator("values")
    def values_must_be_not_empty(cls, v, values):
        if values["type"] != "string" and v is not None:
            raise ValueError("Value list allowed only for string type")

        if v is not None and len(v) < 1:
            raise ValueError("Values must contain at least 1 item")

        return v


    class Config:
        json_encoders = {ObjectId: str}
