import multiprocessing as mp
from typing import List, Optional

from bson import ObjectId

from src.services.upload_images import (
    upload_images_single_product,
    upload_images_many_products
)
from src.apps.products_admin.repository import ProductAdminRepository
from src.utils import async_worker

class ProductImageUploadManager:
    """
    Responsible for managing product image uploads.
    """
    def __init__(self, same_images: bool, images: dict, product_repo: ProductAdminRepository):
        self.same_images = same_images
        self.images = images
        self.product_repo = product_repo

    async def _upload_images_one_product(self, single_product_id: ObjectId):
        """
        Uploads images for a single product to the storage and updates image URLs in the db
        :param single_product_id: product id
        """
        # Upload images for a single product to S3 storage
        image_urls = await upload_images_single_product(single_product_id, self.images)
        # Update the same images URLs for the variations
        await self.product_repo.update_image_links(single_product_id, image_urls.get("images"))

    async def _upload_images_multiple_products(self, parent_id: ObjectId,
                                        variation_ids: List[ObjectId],
                                        variation_images: Optional[List[dict]],
                                        update_parent_images: bool = False):
        """
        Uploads images for multiple products to the storage and updates image URLs in the db.
        """
        # if same_images is False
        if not self.same_images:
            # Upload product images to S3 storage
            image_urls_list = await upload_images_many_products(variation_ids, variation_images)
            # Update images URLs for the variations
            await self.product_repo.update_image_links(
                [i.get("product_id") for i in image_urls_list],
                [i.get("images") for i in image_urls_list]
            )
            if update_parent_images:
                image_dict = {
                    "main": image_urls_list[0].get("images", {}).get("main"),
                    "secondaryImages": None,
                    "sourceProductId": None,
                }
                await self.product_repo.update_image_links(
                    parent_id, image_dict
                )
        else:
            # Upload the same product images for all variations to S3 storage
            image_urls = await upload_images_single_product(parent_id, self.images)
            # Update the same images URLs for the variations
            await self.product_repo.update_image_links([parent_id, *variation_ids],
                                                       image_urls.get("images"),
                                                       same_images=True)

    async def upload_images_one_product(self, single_product_id: ObjectId,
                                           another_process: bool = True):
        """
        Uploads images for a single product to the storage and updates image URLs in the db.
        :param single_product_id: product id
        :param another_process: Whether image uploading should be run in another process or not
        """
        # if run_in_process is True
        if another_process:
            # Execute image uploading in another process
            process = mp.Process(target=async_worker,
                                 args=(self._upload_images_one_product, single_product_id))
            process.start()
        else:
            # Otherwise, execute image uploading in the same process
            await self._upload_images_one_product(single_product_id)

    async def upload_images_multiple_products(self, parent_id: ObjectId,
                                        variation_ids: List[ObjectId],
                                        variation_images: Optional[List[dict]],
                                        update_parent_images: bool = False,
                                        another_process: bool = False):
        """
        Uploads images for multiple products to the storage and updates image URLs in the db.
        :param parent_id: ID of the parent product
        :param variation_ids: List of variation IDs
        :param variation_images: List of images for variations
        :param update_parent_images: Do function need to update parent's image URLs
        :param another_process: Whether image uploading should be run in another process or not
        """
        # if another_process is True
        if another_process:
            # Execute image uploading in another process
            process = mp.Process(target=async_worker,
                                 args=(self._upload_images_multiple_products,
                                       parent_id, variation_ids, variation_images, update_parent_images))
            process.start()
        else:
            # Otherwise, execute image uploading in the same process
            await self._upload_images_multiple_products(parent_id, variation_ids,
                                                        variation_images, update_parent_images)
