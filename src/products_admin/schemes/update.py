from typing import List, Optional, TypedDict, Union
from pydantic import BaseModel, Field
from src.products.schemes.base import Attr, BaseAttrs, ProductVariation
from .create import ImagesCreateProduct
from src.schemes import PyObjectId


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


class ExtraProductDataUpdate(TypedDict):
    """
    Used to provide extra data to product update data
    """
    parent: bool
    same_images: bool
