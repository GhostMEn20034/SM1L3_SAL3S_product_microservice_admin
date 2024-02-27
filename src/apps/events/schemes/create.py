from datetime import datetime, timezone
from pydantic import validator
from .base import EventBase, EventStatusEnum

class CreateEvent(EventBase):
    status: EventStatusEnum = EventStatusEnum.created.value
    image: str

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

    class Config:
        use_enum_values = True

