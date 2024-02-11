from typing import List, Dict

from .product_replication_preparer import ProductReplicationPreparer

async def replicate_single_created_product(product_data: Dict):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_created_single_product(product_data)
    print(prepared_data)


async def replicate_created_variations(variations: List[Dict]):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_created_variations(variations)
    print(prepared_data)


async def replicate_single_updated_product(product_data: Dict):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_updated_single_product(product_data)
    print(prepared_data)

async def replicate_updated_variations(variations: List[Dict]):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_updated_variations(variations)
    print(prepared_data)
