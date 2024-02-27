from pydantic import BaseModel, validator, constr
from typing import List, Union, Optional
from bson import ObjectId

from src.apps.categories.schemes import CategoryForChoices
from src.apps.facets.schemes import Facet
from src.apps.variaton_themes.schemes import VariationTheme
from src.apps.facet_types.schemes import FacetType
from src.apps.products_base.schemes.base import Attr, BaseAttrs, ProductVariation, VariationThemeInProduct
from src.schemes.py_object_id import PyObjectId


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


class ImagesCreateProduct(BaseModel):
    """
    Represents images in create product form
    """
    # Since products is not created yet, they don't have ids.
    # So we will use indexes to determine from what product we need to copy images
    # before products will be created. When we upload images to the storage,
    # server will replace indexes with ObjectId
    sourceProductId: Optional[int]
    main: Optional[str]
    secondaryImages: Optional[List[str]]

    @validator("main")
    def validate_main(cls, v, values):
        if v is None and values.get("sourceProductId") is None:
            raise ValueError("Main Image required")
        return v


class ProductVariationCreateProduct(ProductVariation):
    """
    Represents product variation in create product form
    """
    images: Optional[ImagesCreateProduct]


class CreateProduct(BaseModel):
    """Represents data to create a product"""
    # List of the product attributes (Properties)
    attrs: List[Attr]
    # Product base attributes such as name, price etc.
    base_attrs: BaseAttrs
    # List of the attributes to provide additional information
    extra_attrs: Optional[List[Attr]]
    # keywords to improve the accuracy of product searching
    search_terms: List[constr(min_length=1, strip_whitespace=True, to_lower=True)]
    # Category to which the product belongs
    category: PyObjectId
    # determines whether product has variations
    has_variations: bool
    # Object that stores main image and list of secondary images
    images: Optional[ImagesCreateProduct]
    # Determines whether product variations has the same images
    same_images: bool
    # Determines whether product's attributes can be used in filters
    is_filterable: bool
    # used to define differences between variations (Uses only if product has variations)
    variation_theme: Optional[VariationThemeInProduct]
    # List of product variations
    variations: Optional[List[ProductVariationCreateProduct]]

    @validator("variation_theme")
    def check_variation_theme(cls, v, values):
        """
        Raises an error if the has_variations field is true and there's no variation theme
        """
        if values.get("has_variations") and not v:
            raise ValueError("Variation theme required")
        return v

    @validator("variations")
    def check_variations(cls, v, values):
        """
        Raises an error if the has_variations field is true and there are no product variations
        """
        if values.get("has_variations") and not v:
            raise ValueError("Variations required")
        return v

    @validator("search_terms")
    def check_search_terms(cls, v):
        if len(v) > 30:
            raise ValueError("There can be no more than 30 search terms")
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

