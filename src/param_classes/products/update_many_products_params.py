from typing import List
from bson import ObjectId


class UpdateManyProductsParams:
    """
    :param parent_id: Identifier of the parent product
    :param data: New product data.
    :param product_before_update: Product data before update
    :param images: Images associated with parent product and its variations
    :param session: Session object to make db operations inside of transaction.
    """
    def __init__(self, parent_id: ObjectId,
                 data: dict, product_before_update: dict,
                 new_attrs: List[dict], images: dict,
                 session=None):

        self.parent_id = parent_id
        self.data = data
        self.new_attrs = new_attrs
        self.product_before_update = product_before_update
        self.images = images
        self.session = session
