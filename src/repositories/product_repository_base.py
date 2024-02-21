from pymongo.errors import BulkWriteError
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult, BulkWriteResult
from pymongo.operations import UpdateOne
from pymongo import ReturnDocument
from typing import Optional, Union
from src.config.database import db
from src.logger import logger


class ProductRepositoryBase:
    async def get_product_list(self, filters: Optional[dict] = None, projection: Optional[dict] = None,
                              skip: int = 0,
                              limit: int = 0,
                              **kwargs) -> list:
        """
            Returns a list of products.
            Params:
            :param filters: - A query that matches documents.
            :param projection: - Dictionary with fields must be included in the result
            :param skip: - Number of products to skip
            :param limit: - Number of products to return
            :param kwargs: Other parameters such as session for transaction etc.
        """
        # If filters is not specified, then set filters to empty dict
        if filters is None:
            filters = {}
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        products = await db.products \
            .find(filters, projection, **kwargs).skip(skip).limit(limit).to_list(length=None)

        return products

    async def get_one_product(self, filters: dict, projection: Optional[dict] = None, **kwargs):
        """
           Find a specific product by the given filter
           Params:
           :param filters: - A query that matches the document.
           :param projection: - Dictionary with fields must be included in the result
           :param kwargs: Other parameters such as session for transaction etc.
        """
        # If projection is not specified, then set projection to empty dict
        if projection is None:
            projection = {}

        product = await db.products.find_one(filters, projection, **kwargs)
        return product

    async def create_one_product(self, data: dict, **kwargs) -> InsertOneResult:
        """
            Create a new product.
            Params:
            :param data: Dictionary with product data
            :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_product = await db.products.insert_one(document=data, **kwargs)
        return created_product

    async def create_many_products(self, data: list[dict], **kwargs) -> InsertManyResult:
        """
            Create new products.
            Params:
            :param data: List of dicts with products' data
            :param kwargs: Other parameters for insert such as session for transaction etc.
        """
        if not data:
            raise ValueError("No data provided")

        created_products = await db.products.insert_many(documents=data, **kwargs)
        return created_products

    async def update_one_product(self, filters: dict, data_to_update: Union[list[dict], dict], **kwargs) -> UpdateResult:
        """
            Updates product with specified filters,
            :param filters - A query that matches the document to update
            :param data_to_update - new product properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_product = await db.products.update_one(filter=filters, update=data_to_update, **kwargs)
        return updated_product

    async def update_many_products(self, filters: dict, data_to_update: Union[list[dict], dict],
                                  **kwargs) -> UpdateResult:
        """
            Use this method when you want to set the same data to multiple products
            Updates products with specified filters,
            :param filters - A query that matches documents to update
            :param data_to_update - list of dicts (Pipeline) or dict with new products'
                                    properties and operations on them ($set and so on).
            :param kwargs: Other parameters for update such as session for transaction etc.
        """
        updated_products = await db.products.update_many(filter=filters, update=data_to_update, **kwargs)
        return updated_products

    async def update_many_products_bulk(self, operations: list[UpdateOne], **kwargs) -> BulkWriteResult:
        """
            Use this method when you want to set the different data to different products.
            Performs bulk update of products.
            :param operations: list of UpdateOne operations.
            :param kwargs: Other parameters for bulk write such as order of operations and so on.
        """
        try:
            updated_products = await db.products.bulk_write(operations, **kwargs)
            return updated_products
        except BulkWriteError as bwe:
            logger.error(bwe)

    async def delete_one_product(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes product with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_product = await db.products.delete_one(filter=filters, **kwargs)
        return deleted_product

    async def delete_many_products(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Deletes product with specified filters
        :param filters: - A query that matches the document to delete.
        :param kwargs: Other parameters for delete such as session for transaction etc.
        """
        deleted_product = await db.products.delete_many(filter=filters, **kwargs)
        return deleted_product

    async def find_and_update_one_product(self, filters: dict,
                                          update: Union[list[dict], dict], projection: dict = None,
                                          return_document: str = "before",
                                          **kwargs
                                          ) -> dict:
        """
        Update and return product with specified filters.
        :param filters: A query that matches documents to update
        :param update: list of dicts (Pipeline) or dict with new products'
                               properties and operations on them ($set and so on).
        :param projection: Dictionary with fields must be included in the result.
        :param return_document: If "after", function will return document after update operation.
                                Possible values are: "before", "after".
                                If value is not correct it will be "before"
        :param kwargs: Other parameters for update such as session for transaction, array_filters etc.
        """
        if not projection:
            projection = {}

        return_document_mapping = {
            "before": ReturnDocument.BEFORE,
            "after": ReturnDocument.AFTER,
        }
        return_document = return_document_mapping.get(return_document, ReturnDocument.BEFORE)

        updated_product = await db.products.find_one_and_update(
            filter=filters, update=update, projection=projection,
            return_document=return_document ,**kwargs,
        )

        return updated_product

    async def find_and_delete_one_product(self, filters: dict, projection: dict = None, **kwargs) -> dict:
        """
        Delete and return product with specified filters.
        :param filters: A query that matches documents to delete
        :param projection: Dictionary with fields must be included in the result.
        :param kwargs: Other parameters for delete operation
        """
        if not projection:
            projection = {}

        deleted_product = await db.products.find_one_and_delete(filter=filters, projection=projection, **kwargs)
        return deleted_product
