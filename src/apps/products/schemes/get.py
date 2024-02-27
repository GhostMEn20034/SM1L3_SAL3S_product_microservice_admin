from __future__ import annotations
from decimal import Decimal
from typing import Optional, List, Dict

import fastapi
from bson import ObjectId
from pydantic import BaseModel, Field, constr, condecimal

from src.apps.facets.schemes import Facet
from src.apps.products_base.schemes.base import Product, BaseAttrs, Images, Attr
from src.schemes.py_object_id import PyObjectId


class ProductAdmin(BaseModel):
    """
    Product model for admin panel. Used in the product list model
    """
    # Product identifier
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # Product name
    name: constr(min_length=1)
    # Product price without tax
    price: condecimal(decimal_places=2, ge=Decimal(0))
    # Tax for each product sold
    tax: condecimal(decimal_places=2, ge=Decimal(0))
    # Is product for sale
    for_sale: bool
    # Is the product the parent
    parent: bool
    # List of product children
    variations: Optional[List[ProductAdmin]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class ProductListResponse(BaseModel):
    """
    Response model that returns list of products and other information such as item count, page count etc.
    """
    products: List[ProductAdmin]
    page_count: int
    items_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class Variation(BaseAttrs):
    # Unique identifier for product
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    images: Images
    attrs: List[Attr]


class ProductDetail(Product):
    """
    Represents the product's detailed information.
    """
    # List of product variations
    variations: Optional[List[Variation]]


class CategoryInProduct(BaseModel):
    """
    Represents the category's information in ProductDetailResponse.
    """
    name: str
    groups: Optional[List[str]]

class ProductDetailResponse(BaseModel):
    product: ProductDetail
    facets: Optional[List[Facet]]
    variation_theme: Optional[Dict]
    category: CategoryInProduct
    facet_types: List[Dict]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class ProductSearchFilters(BaseModel):
    category: Optional[List[PyObjectId]] = Field(fastapi.Query([]))
    sku: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}


class ProductSearchResult(BaseModel):
    """
    Each element in product search result
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: constr(min_length=1)
    price: condecimal(ge=Decimal(0), decimal_places=2)
    discount_rate: Optional[condecimal(gt=Decimal(0), max_digits=3, decimal_places=2)]
    sku: constr(min_length=1)


class ProductSearchResponse(BaseModel):
    """
    Represents response of the product search
    """
    products: List[ProductSearchResult]
    page_count: int
    items_count: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}