from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, constr, conint, condecimal, Field

from src.schemes.py_object_id import PyObjectId


class ProductUpdateReplicationSchemaBase(BaseModel):
    """
    Represents replicated data (for other microservices) of updated product
    """
    object_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)
    price: condecimal(ge=Decimal('0.00'), decimal_places=2)
    discount_rate: Optional[condecimal(ge=Decimal('0.00'), decimal_places=2, max_digits=3)]
    tax_rate: condecimal(ge=Decimal('0.00'), decimal_places=2, max_digits=3)
    stock: conint(ge=0)
    max_order_qty: conint(ge=0)
    sku: constr(min_length=1)


class SingleProductUpdateReplicationSchema(ProductUpdateReplicationSchemaBase):
    """Represents replicated data (for other microservices) of the updated single product"""
    for_sale: bool
