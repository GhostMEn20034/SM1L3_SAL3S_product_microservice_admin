import copy
from datetime import datetime
from typing import Union, List
from bson import ObjectId

from src.apps.products.repository import ProductAdminRepository
from src.config.database import client
from src.services.products.replication.replicate_products import (
    replicate_single_updated_product,
    replicate_updated_variations,
    replicate_created_variations,
    replicate_variations_delete,
)
from src.apps.products.utils import form_data_to_update, remove_product_attrs, get_var_theme_field_codes
from src.services.products.image_operation_manager import ImageOperationManager
from src.services.products.product_builder import ProductBuilder
from src.services.products.variation_manager import VariationManager
from src.utils import different_dicts
from src.services.search_terms.replicate_search_terms import replicate_search_terms


class ProductModifier:
    """
    This class is responsible for updating the product
    """
    def __init__(self, product_repo: ProductAdminRepository):
        self.product_repo = product_repo

    async def _update_product_with_variations(self, parent_id: ObjectId, data: dict,
                                              product_before_update: dict, images: dict, session=None):
        same_images = product_before_update.get("same_images")

        variations_common_data = {**product_before_update, "for_sale": True, "is_filterable": True,
                                  "variations": data.get("new_variations"),
                                  "attrs": data.get("attrs", []),
                                  "extra_attrs": data.get("extra_attrs", [])}
        variation_manager = VariationManager(parent_id, self.product_repo, ProductBuilder(variations_common_data))
        if data.get("variations_to_delete", []):
            await variation_manager.delete_variations(data["variations_to_delete"])
            await replicate_variations_delete({"product_ids": data["variations_to_delete"], "parent_ids": []})

        inserted_ids = []
        if data.get("new_variations"):
            inserted_ids, replicated_variations = await variation_manager.handle_variation_inserts(
                variations_common_data, same_images, session)

            await replicate_created_variations(replicated_variations)

        field_codes = await get_var_theme_field_codes(variations_common_data.get("variation_theme", {}))
        # remove parent's attributes
        variations_common_data["attrs"] = await remove_product_attrs(variations_common_data["attrs"], field_codes)
        # Get Attributes that have differences
        different_attrs = different_dicts(variations_common_data["attrs"], product_before_update.get("attrs", []))
        # update all variations
        updated_variation_ids = await variation_manager.handle_variation_updates(
            copy.deepcopy(data.get("old_variations", [])),
            {
                "attrs": different_attrs,
                "extra_attrs": data.get("extra_attrs"),
                "modified_at": datetime.utcnow(),
            },
            same_images,
            images,
            data.get("image_ops", {}),
            inserted_ids,
            session
        )
        # replicate variations
        await replicate_updated_variations(data.get("old_variations", []))

        return updated_variation_ids, inserted_ids

    async def update_product(self, _id: ObjectId, data: dict,
                             parent: bool) -> dict[str, Union[ObjectId, List[ObjectId]]]:
        """
        Updates product(s) in db
        :param _id: Product identifier.
        :param data: VALIDATED new product data
        :param parent: Whether product that will be updated is parent
        """
        data_to_update = form_data_to_update(data, parent)
        # get a product in the state before modifying and update it

        product_before_update = await self.product_repo.find_and_update_one_product(
            {"_id": _id}, {"$set": {**data_to_update, "modified_at": datetime.utcnow()}},
            {"_id": 0, "name": 0, "price": 0, "stock": 0,
             "discount_rate": 0, "tax_rate": 0, "max_order_qty": 0, "sku": 0, "external_id": 0, "modified_at": 0, },
        )
        await replicate_search_terms(data_to_update["search_terms"])

        images = product_before_update.pop("images", {})

        if parent:
            async with (await client.start_session() as session):
                async with session.start_transaction():
                    updated_ids, inserted_ids = await self._update_product_with_variations(
                        _id, data, product_before_update, images, session
                    )
                    return {"product_id": _id, "updated_variation_ids": updated_ids,
                            "inserted_variation_ids": inserted_ids}

        # update product images
        update_linked_products = (not product_before_update.get("same_images", False)
                                  and product_before_update.get("parent_id") is not None)

        source_product_id = images.get("sourceProductId")
        image_operation_manager = ImageOperationManager(_id if source_product_id is None else source_product_id,
                                                        images, data.get("image_ops", {}), self.product_repo)
        await image_operation_manager.update_images_one_product(update_linked_products, another_process=True)
        # replicate an updated product
        await replicate_single_updated_product({"_id": _id, **data_to_update})

        return {"product_id": _id, "updated_variation_ids": None, "inserted_variation_ids": None}
