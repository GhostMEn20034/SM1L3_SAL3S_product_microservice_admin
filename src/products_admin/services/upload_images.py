from typing import List
from src.settings import BUCKET_BASE_URL
from src.services.upload_images import (
    update_image_links,
    upload_imgs_single_prod,
    upload_imgs_many_prods
)
from src.schemes import PyObjectId
import asyncio

def upload_product_photos(
        product_data: dict,
        parent: PyObjectId,
        product_variations: List[PyObjectId],
        images_to_upload: List[dict],
        ):

    async def helper():
        """
        A helper function that uploads product photos to the storage and updates image URLs in the db.
        """
        # if same_images if False
        if not product_data.get("same_images"):
            # Update images URLs for the parent product
            await update_image_links(parent,
                                     {
                                         "main": f"{BUCKET_BASE_URL}/products/{product_variations[0]}_0.jpg",
                                         "secondaryImages": None
                                     },
                                     )
            # Upload product images to S3 storage
            image_urls_list = await upload_imgs_many_prods(product_variations, images_to_upload)
            # Update images URLs for the variations
            await update_image_links(product_variations, [i.get("images") for i in image_urls_list])
        else:
            # Upload the same product images for all variations to S3 storage
            image_urls = await upload_imgs_single_prod(parent, product_data.get("images"))
            # Update the same images URLs for the variations
            await update_image_links([parent, *product_variations], image_urls.get("images"),
                                     same_images=True)

    asyncio.run(helper())


def upload_photos_single_product(single_product: PyObjectId, product_data: dict):

    async def helper():
        """
        A helper function that uploads photos for a single product to the storage and updates image URLs in the db.
        """
        # Upload images for a single product to S3 storage
        image_urls = await upload_imgs_single_prod(single_product, product_data.get("images"))
        # Update the same images URLs for the variations
        await update_image_links(single_product, image_urls.get("images"))

    asyncio.run(helper())