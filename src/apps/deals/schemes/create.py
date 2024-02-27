from decimal import Decimal
from typing import Optional, List
from pydantic import constr, condecimal, validator

from .base import ParentDealBase, DealFilterValues
from src.schemes.py_object_id import PyObjectId


class CreateDealSchema(ParentDealBase):
    image: str
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
