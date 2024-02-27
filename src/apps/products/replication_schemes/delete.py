from typing import List, Optional
from pydantic import BaseModel

from src.schemes.py_object_id import PyObjectId


class DeleteProductsSchema(BaseModel):
    product_ids: Optional[List[PyObjectId]]
    parent_ids: Optional[List[PyObjectId]]
