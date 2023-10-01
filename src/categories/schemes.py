from __future__ import annotations
from pydantic import BaseModel, Field, validator
from src.schemes import PyObjectId
from bson import ObjectId
from typing import Union, List, Optional

class CategoryForChoices(BaseModel):
    """
    Category model for selection in forms
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    groups: Optional[List[str]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class Category(BaseModel):
    """
    Category model
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    level: int
    tree_id: PyObjectId
    parent_id: Union[PyObjectId, None]
    groups: Optional[List[str]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}

class CategoryAdminPanelList(BaseModel):
    result: List[Category]
    page_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class CategoryForm(BaseModel):
    """Category model for forms"""
    name: str
    parent_id: Optional[PyObjectId]
    groups: Optional[List[str]]

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if len(v) < 1:
            raise ValueError("Category name must contain at least 1 character")

        return v


class CategoryUpdate(CategoryForm):
    pass


class CategoryCreate(CategoryForm):
    pass


class CategoryListPublic(Category):
    children: List[CategoryListPublic]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}