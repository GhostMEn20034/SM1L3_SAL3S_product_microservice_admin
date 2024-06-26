from typing import List, Tuple, Optional
from bson import ObjectId
from pymongo.operations import UpdateOne

from src.apps.products.repository import ProductAdminRepository
from src.services.product_query_builder import ProductQueryBuilder
from .product_image_upload_manager import ProductImageUploadManager
from .image_operation_manager import ImageOperationManager
from .product_builder import ProductBuilder
from src.apps.products.utils import get_var_theme_field_codes, remove_product_attrs
from src.services.products.replication.create_variations_replica import create_variations_replica
from src.services.upload_images import delete_many_files_in_s3
from src.config.settings import S3_BUCKET_NAME
from ...param_classes.products.handle_variation_updates_params import HandleVariationUpdatesParams


class VariationManager:
    """
    Responsible for Insert, Update, and Delete variations
    """

    def __init__(self, parent_id: ObjectId, product_repo: ProductAdminRepository, product_builder: ProductBuilder):
        self.product_repo = product_repo
        self.parent_id = parent_id
        self.product_builder = product_builder

    async def upload_variation_images(self, same_images: bool, images: dict,
                                      variation_ids: List[ObjectId], variation_images: Optional[List[dict]] = None,
                                      update_parent_images: bool = False,
                                      another_process: bool = True):
        image_upload_manager = ProductImageUploadManager(same_images,
                                                         images,
                                                         product_repo=self.product_repo)
        # Upload images in another process
        await image_upload_manager.upload_images_multiple_products(self.parent_id,
                                                                   variation_ids,
                                                                   variation_images,
                                                                   update_parent_images,
                                                                   another_process=another_process)

    async def insert_variations(self, parent_id: ObjectId,
                                same_images: bool = False, session=None) -> (
            Tuple)[List[ObjectId], Optional[List[dict]], List[dict]]:
        """
        Insert new product variations.
        :param parent_id: Identifier of the parent product
        :param same_images: Do products have the same images
        :param session: session used to start the transaction.
        """
        variation_data, variation_images = await self.product_builder \
            .build_product_variations(parent_id, return_images=not same_images)
        # Insert product variations
        inserted_variations = await self.product_repo.create_many_products(variation_data, session=session)
        variation_ids = inserted_variations.inserted_ids

        image_sources = None
        if not same_images:
            image_sources = [image.get('sourceProductId') for image in variation_images]

        replicated_variations = await create_variations_replica(variation_ids, variation_data, image_sources)

        return variation_ids, variation_images, replicated_variations

    async def _update_variations(self, variations: List[dict], extra_data_to_update: dict,
                                 session=None) -> List[ObjectId]:
        """
        Internal helper function to update product variations.
        :param variations: List of variations with their base attributes.
        :param extra_data_to_update: Additional data to update variations (new attrs, old attrs, extra_attrs fields)
        :param session: session used to start the transaction.
        """
        updated_ids = []
        operations = []
        push_operation = {}
        array_filters = None

        if attrs := extra_data_to_update.pop("attrs", []):
            query_builder = ProductQueryBuilder()
            set_operator_data, array_filters = await query_builder.build_update_variations_attrs(attrs)
            extra_data_to_update.update(set_operator_data)

        if new_attrs := extra_data_to_update.pop("new_attrs", []):
            push_operation.update(
                {"attrs": {
                    "$each": new_attrs,
                }},
        )

        for variation in variations:
            variation_id = variation.pop("_id")
            if variation_id:
                set_attrs_operation = UpdateOne(
                    {"_id": variation_id, "parent_id": self.parent_id},
                    {
                        "$set": {**variation, **extra_data_to_update},
                    },
                    array_filters=array_filters
                )
                operations.append(set_attrs_operation)
                if push_operation:
                    push_attrs_operation = UpdateOne(
                        {"_id": variation_id, "parent_id": self.parent_id},
                        {"$push": push_operation}
                    )
                    operations.append(push_attrs_operation)

                updated_ids.append(variation_id)

        if operations:
            await self.product_repo.update_many_products_bulk(operations, session=session)

        return updated_ids

    async def update_variations(self, data: List[dict], extra_data_to_update, session=None):
        updated_variation_ids = await self._update_variations(data, extra_data_to_update, session=session)
        return updated_variation_ids

    async def handle_variation_inserts(self, variations_common_data: dict,
                                       same_images: bool,
                                       session=None) -> Tuple[List[ObjectId], List[dict]]:
        """
        Handles inserting new variations into DB for EXISTED variations
        """
        # Insert new variations if user provide them
        # and upload images for them
        field_codes = await get_var_theme_field_codes(variations_common_data.get("variation_theme", {}))
        # remove parent's attributes
        variations_common_data["attrs"] = await remove_product_attrs(variations_common_data["attrs"], field_codes)
        inserted_ids, variation_images, replicated_variations = await self.insert_variations(self.parent_id,
                                                                                             same_images, session)
        if not same_images:
            await self.upload_variation_images(False, {}, inserted_ids, variation_images)
        return inserted_ids, replicated_variations

    async def handle_variation_updates(self, params: HandleVariationUpdatesParams):
        """
        Handles updating variations in DB
        """
        updated_variation_ids = await self.update_variations(
            params.old_variations,
            params.extra_data_to_update,
            params.session
        )
        image_operation_manager = ImageOperationManager(self.parent_id, params.images,
                                                        params.image_ops, self.product_repo)
        if params.same_images:
            await image_operation_manager.update_images_multiple_products([*updated_variation_ids,
                                                                           *params.inserted_ids],
                                                                          another_process=True)
        return updated_variation_ids

    async def delete_variations(self, variation_ids: List[ObjectId], session=None) -> int:
        """
        :param variation_ids: List of variation identifiers
        :param session: session to have a capability to delete the variations inside the transaction.
        """
        variations_to_delete_data = await self.product_repo.get_product_list({"_id": {"$in": variation_ids}},
                                                                             {"same_images": 1, "images": 1})
        deleted_variations = await self.product_repo.delete_many_products({"_id": {"$in": variation_ids}},
                                                                          session=session)
        for deleted_variation in variations_to_delete_data:
            if (deleted_variation.get("images", {}).get("sourceProductId") is None
                    and not deleted_variation.get("same_images", False)):
                main_image = deleted_variation.get("images", {}).get("main")

                secondary_images = deleted_variation["images"]["secondaryImages"] \
                    if deleted_variation.get("images", {}).get("secondaryImages", []) else []

                objects_to_delete = ImageOperationManager. \
                    form_a_list_of_objects_to_delete([main_image, *secondary_images])
                await delete_many_files_in_s3(S3_BUCKET_NAME, objects_to_delete)

        return deleted_variations.deleted_count
