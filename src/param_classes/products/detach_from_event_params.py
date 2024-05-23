from typing import List

from bson import ObjectId

class DetachFromEventParams:
    """
    Parameters for detaching products from an event.
     - event_id: The identifier of the event by which products to detach are being found.
     - product_ids: List of product ids where we need to replicate discounts removal
    """
    def __init__(self, event_id: ObjectId, product_ids: List[ObjectId]):
        self.event_id = event_id
        self.product_ids = product_ids
