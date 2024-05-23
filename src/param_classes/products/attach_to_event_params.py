from decimal import Decimal
from typing import List, Optional, Union

from bson import ObjectId, Decimal128


class AttachToEventParams:
    """
    Parameters for attaching products to an event.
     - product_ids: List of product ids where the method need to update discounts
     - discounts: List of product discounts which the method need to apply to the products.
     - event id: What identifier of the event need to be added to the products.
    """
    def __init__(self, product_ids: List[ObjectId], event_id: ObjectId,
                 discounts: Optional[List[Union[Decimal, Decimal128]]] = None):
        self.product_ids = product_ids
        self.event_id = event_id
        self.discounts = discounts
