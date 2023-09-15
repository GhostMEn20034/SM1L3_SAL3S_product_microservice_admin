from pydantic import BaseModel, Field, constr, validator
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
    units: Optional[List[str]]
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
    name: constr(min_length=1) = Field(...)
    optional: bool
    show_in_filters: bool
    categories: Union[List[PyObjectId], str]
    units: Optional[List[str]]
    values: Optional[List[Any]]

    @validator("categories")
    def categories_must_be_not_empty(cls, v):
        if not len(v) > 0 and not v == "*":
            raise ValueError("Categories must contain at least 1 item")
        return v

    @validator("values")
    def values_must_be_not_empty(cls, v):
        if v is not None and not len(v) > 0:
            raise ValueError("Values must contain at least 1 item")
        return v

    class Config:
        json_encoders = {ObjectId: str}

class FacetCreate(BaseModel):
    code: constr(min_length=1) = Field(...)
    name: constr(min_length=1) = Field(...)
    type: constr(min_length=1) = Field(...)
    values: Optional[List[Any]]
    categories: Union[List[PyObjectId], str]
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
        if values["type"] == "list" and not len(v) > 0:
            raise ValueError("Values must contain at least 1 item")
        return v

    class Config:
        json_encoders = {ObjectId: str}
