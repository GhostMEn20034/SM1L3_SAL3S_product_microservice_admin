from decimal import Decimal
from typing import List, Optional

from bson import ObjectId

from src.apps.products_admin.replication_schemes.create import ProductCreateReplicationSchema
from src.apps.products_admin.replication_schemes.update import (
    SingleProductUpdateReplicationSchema,
    ProductUpdateReplicationSchemaBase,
    ProductIdsToDiscountsMapping,
)
from src.apps.products_admin.replication_schemes.delete import DeleteProductsSchema

from src.services.create_image_name import create_product_image_name


class ProductReplicationPreparer:
    """
    Responsible for preparing product data for the replication
    """
    @staticmethod
    async def prepare_data_of_created_single_product(product_data: dict) -> ProductCreateReplicationSchema:
        if not product_data.get("image"):
            product_data["image"] = create_product_image_name(product_data.get("_id"))

        prepared_data = ProductCreateReplicationSchema.parse_obj(product_data)
        return prepared_data

    @staticmethod
    async def prepare_data_of_created_variations(variations: List[dict]) -> List[ProductCreateReplicationSchema]:
        prepared_variations = []
        for variation in variations:
            if not variation.get("image"):
                variation["image"] = create_product_image_name(variation.get("_id"))

            prepared_variation = ProductCreateReplicationSchema.parse_obj(variation)
            prepared_variations.append(prepared_variation)

        return prepared_variations

    @staticmethod
    async def prepare_data_of_updated_single_product(product_data: dict) -> SingleProductUpdateReplicationSchema:
        prepared_data = SingleProductUpdateReplicationSchema.parse_obj(product_data)
        return prepared_data

    @staticmethod
    async def prepare_data_of_updated_variations(variations: List[dict]) -> List[ProductUpdateReplicationSchemaBase]:
        prepared_variations = []
        for variation in variations:
            prepared_variation = ProductUpdateReplicationSchemaBase.parse_obj(variation)
            prepared_variations.append(prepared_variation)

        return prepared_variations

    @staticmethod
    async def prepare_filters_to_delete_single_product(product_id: ObjectId) -> ObjectId:
        if ObjectId.is_valid(product_id):
            return product_id

        raise ValueError("Invalid product_id")

    @staticmethod
    async def prepare_filters_to_delete_multiple_products(filters: dict) -> DeleteProductsSchema:
        return DeleteProductsSchema.parse_obj(filters)

    @staticmethod
    async def prepare_data_update_product_discounts(product_ids: List[ObjectId],
                                                    discounts: Optional[List[Decimal]]) -> ProductIdsToDiscountsMapping:
        return ProductIdsToDiscountsMapping.parse_obj({"product_ids": product_ids, "discounts": discounts})
