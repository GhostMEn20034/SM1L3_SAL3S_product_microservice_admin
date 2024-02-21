from typing import List

from src.apps.products_admin.replication_schemes.create import ProductCreateReplicationSchema
from src.apps.products_admin.replication_schemes.update import (
    SingleProductUpdateReplicationSchema,
    ProductUpdateReplicationSchemaBase
)
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
