from bson import ObjectId
from src.schemes import PyObjectId
from typing import List, Union
from pydantic import BaseModel, Field ,constr


class VariationThemeFilter(BaseModel):
    name: constr(min_length=1) = Field(...)
    field_codes: List[str]


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
