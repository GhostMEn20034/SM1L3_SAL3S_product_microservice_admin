import multiprocessing as mp
import io
from typing import Optional, Tuple
from urllib.parse import urlparse
from bson import ObjectId

from src.utils import get_image_from_base64, async_worker
from src.services.upload_images import delete_many_files_in_s3, upload_file_to_s3
from src.settings import S3_BUCKET_NAME, BUCKET_BASE_URL
from src.products_admin.repository import ProductAdminRepository

class ImageOperationManager:
    """
    Response for deleting, replacing, adding images to product(s)
    """
    def __init__(self, product_id: ObjectId, images: dict,
                 image_operations: dict, product_repo: ProductAdminRepository):
        self.product_id = product_id
        self.images = images
        self.image_operations = image_operations
        self.product_repo = product_repo

    def _get_image_number(self, image_name: str) -> int:
        """
        Extracts a number from the image name | url (Number before file extension).
        """
        image_path = urlparse(image_name).path[1:]
        number_and_extension = image_path.rsplit(".", 1)
        # Extract the number before the dot
        image_number = int(number_and_extension[0].split("_")[-1])  # Get the last part after the underscore
        return image_number

    @staticmethod
    def form_a_list_of_objects_to_delete(images: list[str]) -> list[dict]:
        """
        :param images: List of image urls.
        :return: List of dictionaries that contain image name and other metadata about image
        """
        objects_to_delete = []
        for image in images:
            # extract image path from the image url
            image_path = urlparse(image).path[1:]
            image_obj = {
                "Key": image_path,
            }
            objects_to_delete.append(image_obj)

        return objects_to_delete

    async def _replace_image(self, new_image: str, name: str):
        """
        Internal helper method for replacing an existing image
        :param new_image: base64 encoded string
        :param name: name of the image we want to replace
        """
        image_bytes = await get_image_from_base64(new_image)
        image_bytes_io = io.BytesIO(image_bytes)
        await upload_file_to_s3(name, image_bytes_io, S3_BUCKET_NAME)

    async def _add_image(self, new_image: str, number: int):
        """
        Internal helper method for adding an image
        :param new_image: base64 encoded string
        :param number: Number of the image to add
        """
        image_name = f"products/{self.product_id}_{number}.jpg"
        image_bytes = await get_image_from_base64(new_image)
        image_bytes_io = io.BytesIO(image_bytes)
        await upload_file_to_s3(image_name, image_bytes_io, S3_BUCKET_NAME)
        image_url = BUCKET_BASE_URL + "/" + image_name
        return image_url

    async def delete_many_images(self) -> Optional[int]:
        images_to_delete = self.image_operations.get("delete", [])
        if self.images.get("secondaryImages") and images_to_delete:
            # Remove secondary images which present in images_to_delete list
            self.images["secondaryImages"] = [image for image in self.images.get("secondaryImages")
                                              if image not in images_to_delete]
            # if secondary images array is empty the assign secondaryImages to None
            if not self.images["secondaryImages"]:
                self.images["secondaryImages"] = None
            objects_to_delete = self.form_a_list_of_objects_to_delete(images_to_delete)
            response = await delete_many_files_in_s3(S3_BUCKET_NAME, objects_to_delete)
            deleted_count = sum(1 for _ in response["Deleted"])
            return deleted_count

    async def replace_images(self) -> Tuple[int, int]:
        main_image_replaced = 0
        secondary_images_replaced = 0
        main_image_replace = self.image_operations.get("replace", {}).get("main")
        secondary_images_replace = self.image_operations.get("replace", {}).get("secondaryImages")

        if main_image_replace:
            main_image_path = urlparse(self.images.get("main")).path[1:]
            await self._replace_image(main_image_replace, main_image_path)
            main_image_replaced = 1

        if secondary_images_replace:
            for secondary_image in secondary_images_replace:
                secondary_image_path = urlparse(secondary_image.get("source")).path[1:]
                await self._replace_image(secondary_image.get("newImg"), secondary_image_path)
                secondary_images_replaced += 1

        return main_image_replaced, secondary_images_replaced

    async def add_images(self):
        images_to_add = self.image_operations.get("add", [])

        if images_to_add:
            image_urls = []
            secondary_images = [] if not self.images.get("secondaryImages") else self.images["secondaryImages"]
            if secondary_images:
                last_secondary_image = secondary_images[-1]
                image_number = self._get_image_number(last_secondary_image)
            else:
                image_number = 0

            for image in images_to_add:
                image_url = await self._add_image(image, image_number + 1)
                image_urls.append(image_url)
                image_number += 1

            secondary_images.extend(image_urls)
            self.images["secondaryImages"] = secondary_images

    async def perform_operations(self):
        await self.delete_many_images()
        await self.replace_images()
        await self.add_images()

    async def _update_images_one_product(self, update_linked_products: bool):
        """Helper function to update images in existed product"""
        await self.perform_operations()
        await self.product_repo.update_image_links(self.product_id, self.images,
                                                   update_linked_products=update_linked_products)

    async def update_images_one_product(self, update_linked_products: bool = False, another_process: bool = False):
        """
        Performs operations on images and
        Updates the image links for a single product in the database
        """
        if another_process:
            process = mp.Process(target=async_worker, args=(self._update_images_one_product, update_linked_products))
            process.start()
        else:
            await self._update_images_one_product(update_linked_products)

    async def _update_images_multiple_products(self, variation_ids: list[ObjectId]):
        """Helper function to update images in product variations"""
        await self.perform_operations()
        await self.product_repo.update_image_links([self.product_id, *variation_ids],
                                                   self.images, same_images=True)

    async def update_images_multiple_products(self, variation_ids: list[ObjectId],
                                                        another_process: bool = False):
        """
        Performs operations on images and
        updates the image links for multiple products if all siblings have the same images
        USE THIS FUNCTION ONLY IF SIBLINGS HAVE THE SAME IMAGES
        """
        if another_process:
            # Execute image uploading in another process
            process = mp.Process(target=async_worker,
                                 args=(self._update_images_multiple_products, variation_ids))
            process.start()
        else:
            await self._update_images_multiple_products(variation_ids)
