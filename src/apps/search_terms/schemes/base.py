from datetime import datetime
from pydantic import BaseModel, constr, conint, Field

from src.schemes.py_object_id import PyObjectId


class SearchTermBase(BaseModel):
    name: constr(min_length=1, strip_whitespace=True, to_lower=True)
    search_count: conint(ge=0) = 0
    last_searched: datetime


class SearchTerm(SearchTermBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
