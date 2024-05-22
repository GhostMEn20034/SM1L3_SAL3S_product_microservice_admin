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
from src.apps.products.utils import form_data_to_update, remove_product_attrs, get_var_theme_field_codes, get_new_attrs
from src.services.products.image_operation_manager import ImageOperationManager
from src.services.products.product_builder import ProductBuilder
from src.services.products.variation_manager import VariationManager
from src.utils import different_dicts
from src.services.search_terms.replicate_search_terms import replicate_search_terms
from src.param_classes.products.update_many_products_params import UpdateManyProductsParams
from src.param_classes.products.handle_variation_updates_params import HandleVariationUpdatesParams


class ProductModifier:
    """
    This class is responsible for updating the product
    """
    def __init__(self, product_repo: ProductAdminRepository):
        self.product_repo = product_repo

    async def _update_product_with_variations(self, params: UpdateManyProductsParams):
        """
        Updates parent product with its variations.
        """
        same_images = params.product_before_update.get("same_images")

        variations_common_data = {**params.product_before_update, "for_sale": True, "is_filterable": True,
                                  "variations": params.data.get("new_variations"),
                                  "search_terms": params.data.get("search_terms", []),
                                  "attrs": params.data.get("attrs", []),
                                  "extra_attrs": params.data.get("extra_attrs", [])}
        variation_manager = VariationManager(params.parent_id, self.product_repo, ProductBuilder(variations_common_data))
        if params.data.get("variations_to_delete", []):
            await variation_manager.delete_variations(params.data["variations_to_delete"])
            await replicate_variations_delete({"product_ids": params.data["variations_to_delete"], "parent_ids": []})

        inserted_ids = []
        if params.data.get("new_variations"):
            inserted_ids, replicated_variations = await variation_manager.handle_variation_inserts(
                variations_common_data, same_images, params.session)

            await replicate_created_variations(replicated_variations)

        field_codes = await get_var_theme_field_codes(variations_common_data.get("variation_theme", {}))
        # remove parent's attributes
        variations_common_data["attrs"] = await remove_product_attrs(variations_common_data["attrs"], field_codes)
        # Get Attributes that have differences
        different_attrs = different_dicts(variations_common_data["attrs"], params.product_before_update.get("attrs", []))
        # update all variations
        handle_variation_updates_params = HandleVariationUpdatesParams(
            old_variations=copy.deepcopy(params.data.get("old_variations", [])),
            extra_data_to_update={
                "new_attrs": params.new_attrs,
                "attrs": different_attrs,
                "extra_attrs": params.data.get("extra_attrs"),
                "modified_at": datetime.utcnow(),
            },
            same_images=same_images, images=params.images,
            image_ops= params.data.get("image_ops", {}),
            inserted_ids=inserted_ids,
            session=params.session,
        )
        updated_variation_ids = await variation_manager.handle_variation_updates(
           handle_variation_updates_params
        )
        # replicate variations
        await replicate_updated_variations(params.data.get("old_variations", []))

        return updated_variation_ids, inserted_ids

    async def update_product(self, _id: ObjectId, data: dict,
                             parent: bool) -> dict[str, Union[ObjectId, List[ObjectId]]]:
        """
        Updates product(s) in db
        :param _id: Product identifier.
        :param data: VALIDATED new product data
        :param parent: Whether product that will be updated is parent
        """
        new_attrs = get_new_attrs(data.get("attrs", []))
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
                    update_many_products_params = UpdateManyProductsParams(
                        parent_id=_id, data=data, new_attrs=new_attrs,
                        product_before_update=product_before_update,
                        images=images, session=session,
                    )
                    updated_ids, inserted_ids = await self._update_product_with_variations(
                        update_many_products_params
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
