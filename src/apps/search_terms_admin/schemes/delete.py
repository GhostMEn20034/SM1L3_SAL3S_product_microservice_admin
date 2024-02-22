from typing import List
from pydantic import BaseModel

from src.schemes.py_object_id import PyObjectId


class DeleteSearchTermsRequest(BaseModel):
    search_terms_ids: List[PyObjectId]
