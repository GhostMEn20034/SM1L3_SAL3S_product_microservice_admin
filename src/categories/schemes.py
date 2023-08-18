from pydantic import BaseModel, Field
from src.schemes import PyObjectId
from bson import ObjectId
from typing import Union

class Category(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    parent: Union[PyObjectId, None]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}
