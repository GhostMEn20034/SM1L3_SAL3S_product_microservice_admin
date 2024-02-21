from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator, conlist, constr

from src.schemes.py_object_id import PyObjectId

class MappingTypeEnum(Enum):
    # Behavior: Treats all tokens within a group as interchangeable.
    # So, searching for any token in the group will match documents containing any other token in the same group.
    equivalent: str = 'equivalent'
    # Behavior: Replaces the input token with all other tokens in the group during the search.
    explicit: str = 'explicit'


class SynonymBaseModel(BaseModel):
    """
    Represents a synonym mappings for mongodb search indexes
    """
    name: constr(min_length=1)
    mappingType: MappingTypeEnum = MappingTypeEnum.equivalent
    input: Optional[List[str]]
    synonyms: conlist(str, min_items=1)

    @validator('input')
    def check_input(cls, v, values):
        # If input is not provided and mappingType is explicit, raise an error
        if not v and values['mappingType'] == MappingTypeEnum.explicit.value:
            raise ValueError('Input Tokens are Required')
        # Otherwise, return the input value
        return v

    class Config:
        use_enum_values = True


class CreatedSynonym(SynonymBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")