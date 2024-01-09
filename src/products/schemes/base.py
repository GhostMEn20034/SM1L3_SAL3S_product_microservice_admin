from typing import Any, Optional, List
from decimal import Decimal

from pydantic import BaseModel, condecimal, constr, conint, Field, validator

from src.schemes import PyObjectId
from src.variaton_themes.schemes import VariationThemeFilter


class BaseAttrs(BaseModel):
    """Represents product base attributes"""
    name: constr(min_length=1) = Field(...)
    price: condecimal(decimal_places=2, ge=Decimal(0))
    # Decimal number that determines discount percentage.
    # For example 0.25 means 25% discount
    discount_rate: Optional[condecimal(max_digits=3, decimal_places=2, le=Decimal(1), ge=Decimal(0))]
    # Decimal number that determines tax percentage.
    # For example 0.02 means that 2% of the price is tax
    tax_rate: condecimal(max_digits=3, decimal_places=2, le=Decimal(1), ge=Decimal(0))
    # Determines the amount of products in stock
    stock: conint(ge=0)
    # Maximum order quantity. Maximum count of product you can order
    max_order_qty: conint(ge=0)
    # Stock Keeping Unit
    sku: constr(min_length=1) = Field(...)
    # External identifier such as Barcode, GTIN, UPC, etc. Not in use now
    external_id: Optional[str]

    @validator("discount_rate")
    def discount_rate_validator(cls, v):
        if v == 0:
            return None

        return v

class VariationThemeInProduct(BaseModel):
    """
    Variation theme in product.
    """
    # variation theme name
    name: constr(min_length=1) = Field(...)
    # Options that determine difference between products
    options: List[VariationThemeFilter]

class Attr(BaseModel):
    """Represents one product attribute (property)"""
    # Slugified attribute name, used in the filters
    code: constr(min_length=1) = Field(...)
    # Attribute name
    name: constr(min_length=1) = Field(...)
    # Attribute value
    value: Any
    # Attribute type, defines attribute value type (string, integer, decimal, etc.)
    type: constr(min_length=1) = Field(...)
    # Used to define whether user can omit this attribute when create a product.
    optional: bool
    # Unit measure of product attribute (GB, Meters, Watt)
    unit: Optional[str]
    # Attribute group, for example, SSD amount belongs to "storage" group
    group: Optional[str]


class Images(BaseModel):
    """Represents product images"""
    # The URL of the main product image if user gets product.
    # if user creates product this field stores base64 encoded image
    main: str
    # List of URLs of the secondary images of the product if user gets product.
    # if user creates product this field stores list of base64 encoded images
    secondaryImages: Optional[List[str]]
    # ID of the product from which images were copied. OPTIONAL
    # If this value is null / None, it is means that product has his own images.
    sourceProductId: Optional[PyObjectId]


class ProductVariation(BaseAttrs):
    """
    Represents a product variations
    """
    # Stores encoded product images
    images: Optional[Images]
    # List of the product attributes (Properties)
    attrs: List[Attr]


class Product(ProductVariation):
    """
    Represents a product instance
    """
    # Unique identifier for product
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # Determines whether product is parent of some products
    parent: bool
    # Unique identifier of the parent product
    parent_id: Optional[PyObjectId]
    # Boolean value, that determines whether product for sale
    for_sale: bool
    # Stores urls to product images
    images: Images
    # A category to which the product belongs
    category: PyObjectId
    # List of the product attributes (Properties)
    extra_attrs: List[Attr]
    # Determines whether product's attributes can be used in filters
    is_filterable: bool
    # Defines whether product has the same images as in other variations
    same_images: bool
    # variation theme, used to define differences between variations (Used only if product has variations)
    variation_theme: Optional[VariationThemeInProduct]
