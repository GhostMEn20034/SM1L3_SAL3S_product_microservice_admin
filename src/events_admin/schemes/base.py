from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import BaseModel, constr, AnyHttpUrl, Field, condecimal, conlist, validator

from src.schemes.py_object_id import PyObjectId


class EventStatusEnum(str, Enum):
    created = "created"
    started = "started"
    ended = "ended"


class DiscountedProduct(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)
    discount_rate: condecimal(gt=Decimal("0.00"), le=Decimal("1.00"), decimal_places=2, max_digits=3)


class EventBase(BaseModel):
    """
    Represents an event model
    """
    name: constr(min_length=1)
    description: Optional[str]
    image: AnyHttpUrl
    start_date: datetime
    end_date: datetime
    status: EventStatusEnum
    discounted_products: conlist(DiscountedProduct, min_items=1)

class Event(EventBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}
