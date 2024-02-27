from typing import List, Optional, TypedDict, Union
from bson import ObjectId
from pydantic import BaseModel, Field, validator, constr

from src.apps.products_base.schemes.base import Attr, BaseAttrs, ProductVariation
from .create import ImagesCreateProduct
from src.schemes.py_object_id import PyObjectId


class ImagesUpdateProduct(ImagesCreateProduct):
    """
    Represent images in new variations of existing product
    """
    sourceProductId: Optional[Union[PyObjectId, int]]


class OldProductVariations(BaseAttrs):
    """
    Old product variations
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class NewProductVariations(ProductVariation):
    """
    New product variations
    """
    images: Optional[ImagesUpdateProduct]


class SecondaryImageReplace(BaseModel):
    """
    Represents replace of secondary images
    """
    # URL of image to replace
    source: str
    # BASE 64 encoded file which will replace old secondary image
    newImg: str
    # Image index on the frontend (used only for error handling)
    index: int

class ImagesReplace(BaseModel):
    """
    Represents replace of product images
    """
    # make main image optional
    main: Optional[str]
    secondaryImages: Optional[List[SecondaryImageReplace]]


class ImageOps(BaseModel):
    """
    Represents image operations:
    - Add
    - Delete
    - Replace
    """
    # List of encoded images to insert
    add: Optional[List[str]]
    # List of links of images to delete
    delete: Optional[List[str]]
    # Object with the new main image and new secondary images. OPTIONAL.
    replace: Optional[ImagesReplace]


class UpdateProduct(BaseModel):
    """
    Represents data to update a product
    """
    # List of the product attributes (Properties)
    attrs: Optional[List[Attr]]
    # Product base attributes such as name, price etc.
    base_attrs: Optional[BaseAttrs]
    # List of the attributes to provide additional information
    extra_attrs: Optional[List[Attr]]
    # keywords to improve the accuracy of product searching
    search_terms: List[constr(min_length=1, strip_whitespace=True, to_lower=True)]
    # Boolean value, that determines whether product for sale
    for_sale: Optional[bool]
    # Determines whether product's attributes can be used in filters
    is_filterable: Optional[bool]
    # Image operations
    image_ops: Optional[ImageOps]
    # New product variations
    new_variations: Optional[List[NewProductVariations]]
    # Old product variations
    old_variations: Optional[List[OldProductVariations]]
    # List of variations to delete
    variations_to_delete: Optional[List[PyObjectId]]

    @validator("attrs")
    def validate_attrs(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("Attribute list must not be empty")
        return v

    @validator("search_terms")
    def check_search_terms(cls, v):
        if len(v) > 30:
            raise ValueError("There can be no more than 30 search terms")
        return v


class ExtraProductDataUpdate(TypedDict):
    """
    Used to provide extra data to product update data
    """
    parent: bool
    same_images: bool


class UpdateProductResponse(BaseModel):
    """
    Represents product update response
    """
    # Identifier of product to update
    product_id: PyObjectId
    # If the product has variations (It is a parent product), the response can contain
    # a list of identifiers of updated and inserted products
    updated_variation_ids: Optional[List[PyObjectId]]
    inserted_variation_ids: Optional[List[PyObjectId]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
