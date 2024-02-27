from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, constr, conlist, validator

from .base import DiscountedProduct


class UpdateEvent(BaseModel):
    name: Optional[constr(min_length=1)]
    description: Optional[str]
    image: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    discounted_products: Optional[conlist(DiscountedProduct, min_items=1)]

    @validator('start_date')
    def validate_start_date(cls, v: datetime):
        if v < datetime.now(tz=timezone.utc):
            raise ValueError("The Start Date must be greater than current time")

        return v

    @validator('end_date')
    def validate_end_date(cls, v: datetime, values):
        if v < datetime.now(tz=timezone.utc):
            raise ValueError("The End Date must be greater than current time")

        if 'start_date' in values and v < values['start_date']:
            # raise a validation error if end_date is earlier than start_date
            raise ValueError('End Date must be later than Start Date')
        return v

