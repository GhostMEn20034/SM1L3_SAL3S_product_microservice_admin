from typing import Union, List, Optional

from bson import ObjectId
from pymongo.operations import UpdateOne

from src.config.database import db
from src.config.settings import ATLAS_SEARCH_INDEX_NAME_PRODUCTS
from src.repositories.product_repository_base import ProductRepositoryBase
from src.aggregation_queries.products.product_details import get_variations_lookup_pipeline, get_product_detail
from src.aggregation_queries.products.product_list import (
    get_product_list_pipeline,
    get_search_products_pipeline_stage,
    get_search_products_main_pipeline,
)


class ProductAdminRepository(ProductRepositoryBase):
    async def update_image_links(self, product_ids: Union[List[ObjectId], ObjectId],
                                 images: Union[List[dict], dict],
                                 same_images: bool = False, update_linked_products: bool = False):
        """
        Updates image links in products.
        :param product_ids: List of ObjectID or ObjectID. Products where image links will be updated.
        :param images: List of dicts or dict. Image links that will be inserted into the products.
        :param same_images: defines whether function should upload the same images to the products.
        :param update_linked_products: defines whether function should update images in the products.
        which use images from the specified product (from product id above)
        """
        # check if the input is a single product id or a list of product ids
        if isinstance(product_ids, list):
            # check if the same_images parameter is True
            if same_images:
                # use the update_many method with the $in operator to update the same images for the products in
                # the product_ids list
                await self.update_many_products(
                    {"_id": {"$in": product_ids}},
                    {"$set": {"images": images}}
                )
            else:
                # List of operations for bulkWrite
                operations = []
                # loop through the product ids and images
                for product_id, image in zip(product_ids, images):
                    # add the update_one method to the list of operations
                    operations.append(UpdateOne(
                        {"_id": product_id},
                        {"$set": {"images": image}}
                    ))
                await self.update_many_products_bulk(operations, ordered=False)
        else:
            if update_linked_products:
                filters = {
                    "$or": [
                        {"_id": product_ids},
                        {"images.sourceProductId": product_ids}
                    ]
                }
                data_to_update = {"images.main": images.get("main"),
                                  "images.secondaryImages": images.get("secondaryImages")}
                await self.update_many_products(filters, {"$set": data_to_update})
            else:
                filters = {"_id": product_ids}
                data_to_update = {"images": images}
                # use the update_one method to update the image links for the single product
                await self.update_one_product(
                    filters,
                    {"$set": data_to_update}
                )

    async def get_product_details(self, product_id: ObjectId) -> dict:
        """
        Returns product details and its variations if they are present.
        """
        # Pipeline that executes on product variations join
        variations_lookup_pipeline = get_variations_lookup_pipeline()
        # Main aggregation pipeline
        pipeline = get_product_detail(product_id, variations_lookup_pipeline)

        product = await db.products.aggregate(pipeline=pipeline).to_list(length=None)
        return product[0] if product else {}

    async def get_products_with_variations(self, page: int, page_size: int) -> dict:
        """
        :param page: page number. Suppose for each page you have 5 items. If the page number is 1,
        then db will return only first 5 items. If the page number is 2, then the database will skip the first 5 items,
        and return 5 items after the previous 5 items.
        :param page_size: count of items per page.
        :return: Products, their variations and count of products.
        """
        # product fields that will be returned by the db
        product_projection = {
            "name": 1,
            "price": 1,
            "for_sale": 1,
            "parent": 1
        }
        pipeline = get_product_list_pipeline(page, page_size, product_projection)
        product_list = await db.products.aggregate(pipeline=pipeline).to_list(length=None)
        return product_list[0] if product_list else {}

    async def search_products_by_name(self, name: str, filters: Optional[dict] = None,
                                      projection: Optional[dict] = None,
                                      page: int = 1, page_size: int = 15, **kwargs) -> dict:
        """
        Search products by the name
        Params:
        :param name: Product name by which to search.
        :param filters: - A query that matches documents.
        :param projection: - Dictionary with fields must be included in the result.
        :param page: page number
        :param page_size: count of items per page.
        :return: Products, their variations and count of products.
        """
        if not filters:
            filters = {}

        if not projection:
            projection = {}

        product_pipeline = []
        main_pipeline = []
        if name:
            main_pipeline.append(
               get_search_products_pipeline_stage(name, ATLAS_SEARCH_INDEX_NAME_PRODUCTS)
            )

        product_pipeline.extend([
            {"$project": projection},
            {
                "$skip": (page - 1) * page_size
            },
            {
                "$limit": page_size
            },
        ])
        main_pipeline.extend(
            get_search_products_main_pipeline(filters, product_pipeline)
        )
        found_products = await db.products.aggregate(pipeline=main_pipeline, **kwargs).to_list(length=None)
        return found_products[0] if found_products else {}
