from typing import TypedDict, List

from .base import ProductItem


class ProductReleaseData(TypedDict):
    products: List[ProductItem]

