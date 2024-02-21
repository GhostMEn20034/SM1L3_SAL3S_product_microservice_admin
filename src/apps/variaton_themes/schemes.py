from bson import ObjectId
from src.schemes.py_object_id import PyObjectId
from typing import List, Union
from pydantic import BaseModel, Field ,constr, validator


class VariationThemeFilter(BaseModel):
    name: str
    field_codes: List[str]

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if len(v) < 1:
            raise ValueError("Filter name must contain at least 1 character")

        return v

    @validator("field_codes")
    def field_codes_must_not_be_empty(cls, v):
        if len(v) < 1:
            raise ValueError("Field codes must contain at least 1 item")
        return v


class VariationTheme(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1) = Field(...)
    filters: List[VariationThemeFilter]
    categories: Union[List[PyObjectId], str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class VariationThemeListAction(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1) = Field(...)


class VariationThemeResult(BaseModel):
    result: List[VariationThemeListAction]
    page_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class VariationThemeUpdate(BaseModel):
    filters: List[VariationThemeFilter]
    categories: Union[List[PyObjectId], str]

    @validator("categories")
    def categories_validator(cls, v):
        if len(v) < 1:
            return "*"

        return v


class VariationThemeCreate(BaseModel):
    name: str
    filters: List[VariationThemeFilter]
    categories: Union[List[PyObjectId], str]

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if len(v) < 1:
            raise ValueError("Variation theme name must contain at least 1 character")

        return v

    @validator("categories")
    def categories_validator(cls, v):
        if len(v) < 1:
            return "*"

        return v