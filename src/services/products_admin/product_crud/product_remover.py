from bson import ObjectId

from src.settings import S3_BUCKET_NAME
from src.products_admin.repository import ProductAdminRepository
from src.services.products_admin.image_operation_manager import ImageOperationManager
from src.services.upload_images import delete_many_files_in_s3


class ProductRemover:
    def __init__(self, product_repo: ProductAdminRepository):
        self.product_repo = product_repo

    def _extract_images_from_dict(self, images: dict) -> list[str]:
        """Extracts main and secondary images from the given dict."""
        main_image = images.get("main")
        secondary_images = images.get("secondaryImages")
        if not secondary_images:
            secondary_images = []

        return [main_image, *secondary_images]

    async def _delete_images(self, images_to_delete: list[str]) -> int:
        """Deletes images from S3."""
        objects_to_delete = ImageOperationManager.form_a_list_of_objects_to_delete(images_to_delete)
        response = await delete_many_files_in_s3(S3_BUCKET_NAME, objects_to_delete)
        return len(response["Deleted"])

    async def delete_images_one_product(self, images: dict) -> int:
        """Deletes images for a single product."""
        images_to_delete = self._extract_images_from_dict(images)
        deleted_count = await self._delete_images(images_to_delete)
        return deleted_count

    async def delete_images_many_products(self, image_list: list[dict]):
        """Deletes images for multiple products."""
        images_to_delete = []
        for image in image_list:
            images_to_delete.extend(self._extract_images_from_dict(image))

        deleted_count = await self._delete_images(images_to_delete)
        return deleted_count

    async def _get_children_images(self, parent_ids: list[ObjectId]) -> list[dict]:
        children = await self.product_repo.get_product_list(
            {"parent_id": {"$in": parent_ids}, "same_images": False},
            {"images": 1})
        image_list = [product.get("images") for product in children
                      if product.get("images", {}).get("sourceProductId") is None]
        return image_list

    async def delete_one_product(self, product_data: dict) -> int:
        same_images = product_data.get("same_images", True)
        # if the product is the parent, then remove it and it's child products
        if product_data.get("parent", True):
            if same_images:
                await self.delete_images_one_product(product_data.get("images", {}))
            else:
                children_images = await self._get_children_images([product_data.get("_id")])
                await self.delete_images_many_products(children_images)

            deleted_products = await self.product_repo.delete_many_products(
                {"$or": [{"_id": product_data.get("_id")}, {"parent_id": product_data.get("_id")}]}
            )
            return deleted_products.deleted_count

        if not same_images and product_data.get("images", {}).get("sourceProductId") is None:
            await self.delete_images_one_product(product_data.get("images", {}))

        deleted_product = await self.product_repo.delete_one_product({"_id": product_data.get("_id")})
        return deleted_product.deleted_count

    async def delete_many_products(self, products: list[dict]) -> int:
        products_ids_to_delete = []
        images_to_delete = []
        parent_ids = []
        for product in products:
            # Is the product the parent
            products_ids_to_delete.append(product.get("_id"))
            # if the product is the parent, then remove it and it's child products
            if product.get("parent", True):
                parent_ids.append(product.get("_id"))
                if product.get("same_images", True):
                    images_to_delete.append(product.get("images"))

            elif not product.get("same_images", False) and product.get("images", {}).get("sourceProductId") is None:
                images_to_delete.append(product.get("images"))

        if parent_ids:
            children_images = await self._get_children_images(parent_ids)
            images_to_delete.extend(children_images)

        if images_to_delete:
            await self.delete_images_many_products(images_to_delete)

        deleted_products = await self.product_repo.delete_many_products(
            {"$or": [
                {"_id": {"$in": products_ids_to_delete}}, {"parent_id": {"$in": parent_ids}}]
            }
        )

        return deleted_products.deleted_count
