from pydantic import BaseModel
from typing import List
from src.facets.schemes import Facet
from src.variaton_themes.schemes import VariationTheme
from bson import ObjectId

class ProductCreateForm(BaseModel):
    """Model that contains facets and variation themes to create a product"""
    facets: List[Facet]
    variation_themes: List[VariationTheme]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}
