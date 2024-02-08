from typing import List

from bson import ObjectId
from pydantic import BaseModel
from .base import Event

class EventsDetailResponse(BaseModel):
    event: Event

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class EventListResponse(BaseModel):
    events: List[Event]
    page_count: int

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}

