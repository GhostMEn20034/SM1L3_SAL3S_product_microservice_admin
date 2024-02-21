from typing import List
from pydantic import BaseModel
from src.schemes.py_object_id import PyObjectId


class DeleteProductRequest(BaseModel):
    """
    Represents a request body for deleting products
    """
    product_ids: List[PyObjectId]
