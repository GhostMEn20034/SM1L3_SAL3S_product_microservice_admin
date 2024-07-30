from typing import TypedDict, List

from .base import ProductItem


class ProductReservationData(TypedDict):
    products: List[ProductItem]
