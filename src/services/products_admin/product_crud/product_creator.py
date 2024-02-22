from typing import Tuple, List, Optional
from bson import ObjectId

from src.config.database import client
from src.apps.products_admin.repository import ProductAdminRepository
from src.apps.products_admin.utils import set_attr_non_optional, get_var_theme_field_codes, remove_product_attrs
from src.services.products_admin.product_builder import ProductBuilder
from src.services.products_admin.product_image_upload_manager import ProductImageUploadManager
from src.services.products_admin.variation_manager import VariationManager
from src.services.products_admin.replication.replicate_products import (
    replicate_single_created_product,
    replicate_created_variations
)
from src.services.search_terms_admin.replicate_search_terms import replicate_search_terms


class ProductCreator:
    """
    This class is responsible for creating the products
    """
    def __init__(self, product_repo: ProductAdminRepository):
        self.product_repo = product_repo

    async def _create_single_product(self, product_data: dict):
        same_images = product_data.get("same_images", True)

        product_builder = ProductBuilder(product_data)
        image_upload_manager = ProductImageUploadManager(same_images,
                                                         product_data.get("images"),
                                                         product_repo=self.product_repo)
        single_product_data = await product_builder.build_single_product()
        # Create single product
        inserted_single_product = await self.product_repo.create_one_product(single_product_data)
        single_product_id = inserted_single_product.inserted_id
        # Replicate created product
        await replicate_single_created_product({"_id": single_product_id, **single_product_data})
        # Upload images in another process
        await image_upload_manager.upload_images_one_product(single_product_id, another_process=True)
        return single_product_id

    async def _create_product_with_variations(self, product_data: dict,
                                              session=None) -> Tuple[ObjectId, List[ObjectId]]:
        same_images = product_data.get("same_images", True)
        product_builder = ProductBuilder(product_data)
        # Set "optional" property to False in each variations' attribute
        for variation in product_data.get("variations"):
            variation["attrs"] = await set_attr_non_optional(variation["attrs"])
        # Build data for parent product
        parent_data = await product_builder.build_single_product(parent=True)
        # Create parent product
        inserted_parent = await self.product_repo.create_one_product(parent_data, session=session)
        parent_id = inserted_parent.inserted_id
        # get variation theme field codes
        field_codes = await get_var_theme_field_codes(product_data.get("variation_theme", {}))
        # remove parent's attributes
        product_data["attrs"] = await remove_product_attrs(product_data["attrs"], field_codes)
        # insert variations to db
        variation_manager = VariationManager(parent_id, self.product_repo, product_builder)
        variation_ids, variation_images, replicated_variations = await variation_manager.insert_variations(
            parent_id, same_images, session)
        # Replicate variations for other microservices
        await replicate_created_variations(replicated_variations)

        await variation_manager.upload_variation_images(same_images, product_data.get("images"),
                                                        variation_ids, variation_images, update_parent_images=True)
        # return parent id and list of inserted products' ids
        return parent_id, variation_ids

    async def create_product(self, product_data: dict) -> Tuple[ObjectId, Optional[List[ObjectId]]]:
        """
        Inserts product(s) to db
        :param product_data: VALIDATED product data to be inserted
        """
        product_data["for_sale"] = True
        has_variations = product_data.get("has_variations", False)
        # Set "optional" property in each product's attribute
        product_data["attrs"] = await set_attr_non_optional(product_data["attrs"])

        if has_variations:
            async with (await client.start_session() as session):
                async with session.start_transaction():
                    parent_id, variation_ids = await self._create_product_with_variations(product_data, session)
                    await replicate_search_terms(product_data["search_terms"], session)
                    return parent_id, variation_ids

        single_product_id = await self._create_single_product(product_data)
        await replicate_search_terms(product_data["search_terms"])
        return single_product_id, None
