from typing import List, Optional, Dict, Union
from bson import ObjectId

from src.services.create_image_name import create_product_image_name


async def create_variations_replica(product_ids: List[ObjectId],
                                    variation_data: List[Dict],
                                    variation_image_sources: Optional[List[Union[ObjectId, int]]] = None) -> List[Dict]:
    """
    Forms data that will be used for product replication (Replication for other microservices)
    :param product_ids: List of product identifiers
    :param variation_data: List of variation data
    :param variation_image_sources: List of variation image sources (From which product images will be copied)

    NOTE: count of products ids and variation data must be the same
    and if you pass variation_image_sources, it must have the same length as products ids and variation_images
    """
    merged_list = []
    for i, (product_id, variation_data_item) in enumerate(zip(product_ids, variation_data)):
        merged_item = {"_id": product_id, **variation_data_item}
        if variation_data_item.get("same_images"):
            merged_item["image"] = create_product_image_name(variation_data_item.get("parent_id"))
        elif variation_image_sources[i] is None:
            merged_item["image"] = create_product_image_name(product_id)
        elif isinstance(variation_image_sources[i], ObjectId):
            merged_item["image"] = create_product_image_name(variation_image_sources[i])
        elif isinstance(variation_image_sources[i], int):
            image_source: ObjectId = product_ids[variation_image_sources[i]]
            merged_item["image"] = create_product_image_name(image_source)

        merged_list.append(merged_item)

    return merged_list