from decimal import Decimal
from typing import Optional, List
from pydantic import constr, condecimal, validator, BaseModel

from .base import DealFilterValues
from src.schemes.py_object_id import PyObjectId


class UpdateDealSchema(BaseModel):
    name: constr(min_length=1, strip_whitespace=True)
    is_visible: bool = False
    parent_id: Optional[PyObjectId]
    image: Optional[str]
    query: Optional[constr(min_length=1, strip_whitespace=True)]
    price_min: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    price_max: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    category_id: Optional[PyObjectId]
    other_filters: Optional[List[DealFilterValues]]

    @validator("price_max")
    def check_price_max(cls, v, values):
        if v is not None and values["price_min"] is not None:
            if v < values["price_min"]:
                raise ValueError("Maximum price must be greater than Minimum price")

        return v


class UpdatedParentDeal(BaseModel):
    """
    Represents a data to update a parent deal
    """
    name: constr(min_length=1, strip_whitespace=True)
    is_visible: bool = False
    image: Optional[str]


class UpdatedDeal(UpdatedParentDeal):
    """
    Represents a data to update a deal
    """
    parent_id: Optional[PyObjectId]
    query: Optional[constr(min_length=1, strip_whitespace=True)]
    price_min: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    price_max: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    category_id: Optional[PyObjectId]
    other_filters: Optional[List[DealFilterValues]]
