from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field, constr, AnyHttpUrl, condecimal, conlist, validator
from datetime import datetime

from src.schemes.py_object_id import PyObjectId


class DealFilterValues(BaseModel):
    code: constr(min_length=1)
    name: constr(min_length=1)
    # This value can be string, decimal, integer, list of: int, decimal, string
    value: Any
    unit: Optional[constr(min_length=1)]
    type: constr(min_length=1)


class ParentDealBase(BaseModel):
    name: constr(min_length=1, strip_whitespace=True)
    is_visible: bool = False
    is_parent: bool
    parent_id: Optional[PyObjectId]

    @validator('parent_id')
    def validate_parent_id(cls, v, values):
        if v is not None and values["is_parent"]:
            raise ValueError("If a Deal is a parent, then parent_id must be None")

        return v

class DealBase(ParentDealBase):
    query: Optional[constr(min_length=1, strip_whitespace=True)]
    price_min: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    price_max: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    category_id: Optional[PyObjectId]
    other_filters: Optional[List[DealFilterValues]]


class ParentDeal(ParentDealBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    image: AnyHttpUrl
    created_at: datetime
    modified_at: datetime


class Deal(ParentDeal, DealBase):
    query_string: str
