from decimal import Decimal
from typing import Optional, Any, Dict, List

from pydantic import BaseModel, constr, condecimal
from src.schemes.py_object_id import PyObjectId


class AttributeFilterElement(BaseModel):
    # This value can be string, decimal, integer, list of: int, decimal, string
    value: Any
    unit: Optional[constr(min_length=1)]

class FacetObject(BaseModel):
    is_range: bool
    values: List[AttributeFilterElement]


class ProductFilters(BaseModel):
    query: Optional[constr(min_length=1, strip_whitespace=True)]
    price_min: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    price_max: Optional[condecimal(decimal_places=2, gt=Decimal(0))]
    category_id: Optional[PyObjectId]
    chosen_facets: Optional[Dict[str, FacetObject]]
