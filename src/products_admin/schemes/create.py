from pydantic import BaseModel, validator
from typing import List, Union, Optional

from src.categories_admin.schemes import CategoryForChoices
from src.facets.schemes import Facet
from src.variaton_themes.schemes import VariationTheme
from src.facet_types.schemes import FacetType
from src.products.schemes.base import Attr, BaseAttrs, Images, ProductVariation

from bson import ObjectId
from src.schemes import PyObjectId


class FacetCreateForm(Facet):
    categories: Optional[Union[List[PyObjectId], str]]


class VariationThemeCreateForm(VariationTheme):
    categories: Optional[Union[List[PyObjectId], str]]

class ProductCreateForm(BaseModel):
    """Model that contains facets and variation themes to create a product"""
    facets: List[FacetCreateForm]
    variation_themes: List[VariationThemeCreateForm]
    facet_types: List[FacetType]
    category: CategoryForChoices

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}

class CreateProduct(BaseModel):
    """Represents data to create a product"""
    # List of the product attributes (Properties)
    attrs: List[Attr]
    # Product base attributes such as name, price etc.
    base_attrs: BaseAttrs
    # List of the attributes to provide additional information
    extra_attrs: Optional[List[Attr]]
    # Category to which the product belongs
    category: PyObjectId
    # determines whether product has variations
    has_variations: bool
    # Object that stores main image and list of secondary images
    images: Optional[Images]
    # Determines whether product variations has the same images
    same_images: bool
    # Determines whether product's attributes can be used in filters
    is_filterable: bool
    # used to define differences between variations (Uses only if product has variations)
    variation_theme: Optional[PyObjectId]
    # List of product variations
    variations: Optional[List[ProductVariation]]

    @validator("images")
    def check_images_if_same_images(cls, v, values):
        """
        Raises error if there's no value AND (same_images is true OR has_variations is false)
        """

        if not v and (values.get("same_images") or not values.get("has_variations")):
            raise ValueError("Images required")

        return v


    @validator("variation_theme")
    def check_variation_theme(cls, v, values):
        """
        Raises error if has_variations is true and there's no variation theme
        """
        if values.get("has_variations") and not v:
            raise ValueError("Variation theme required")

        return v

    @validator("variations")
    def check_variations(cls, v, values):
        """
        Raises error if has_variations is true and there are no product variations
        """
        if values.get("has_variations") and not v:
            raise ValueError("Variation theme required")

        return v


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateProductResponse(BaseModel):
    # ID of the inserted single product or parent product
    product_id: PyObjectId
    # List of IDs of the inserted product variations
    variation_ids: Optional[List[PyObjectId]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

