from typing import List
from bson import ObjectId


class HandleVariationUpdatesParams:
    def __init__(self,
        old_variations: List[dict], extra_data_to_update: dict, same_images: bool,
    images: dict, image_ops: dict, inserted_ids: List[ObjectId], session = None):
        self.old_variations = old_variations
        self.extra_data_to_update = extra_data_to_update
        self.same_images = same_images
        self.images = images
        self.image_ops = image_ops
        self.inserted_ids = inserted_ids
        self.session = session
