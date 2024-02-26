from decimal import Decimal
from typing import List, Dict, Optional
from bson import ObjectId

from src.utils import convert_type
from .product_replication_preparer import ProductReplicationPreparer
from src.message_broker.producer import Producer
from src.config.settings import PRODUCT_CRUD_EXCHANGE_TOPIC_NAME


async def replicate_single_created_product(product_data: Dict):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_created_single_product(product_data)
    prepared_data = prepared_data.dict()
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    convert_type(prepared_data, ObjectId, str)
    convert_type(prepared_data, Decimal, str)

    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.crud.create.one', message=prepared_data)


async def replicate_created_variations(variations: List[Dict]):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_created_variations(variations)
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    prepared_data = [convert_type(variation.dict(), ObjectId, str) for variation in prepared_data]
    prepared_data = [convert_type(variation, Decimal, str) for variation in prepared_data]

    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.crud.create.many', message=prepared_data)


async def replicate_single_updated_product(product_data: Dict):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_updated_single_product(product_data)
    prepared_data = prepared_data.dict()
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    convert_type(prepared_data, ObjectId, str)
    convert_type(prepared_data, Decimal, str)

    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.crud.update.one', message=prepared_data)


async def replicate_updated_variations(variations: List[Dict]):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_updated_variations(variations)
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    prepared_data = [convert_type(variation.dict(), ObjectId, str) for variation in prepared_data]
    prepared_data = [convert_type(variation, Decimal, str) for variation in prepared_data]

    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.crud.update.many', message=prepared_data)


async def replicate_single_product_delete(product_id: ObjectId):
    prepared_data = await ProductReplicationPreparer.prepare_filters_to_delete_single_product(product_id)
    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.crud.delete.one', message={"_id": str(prepared_data)})


async def replicate_variations_delete(filters: dict):
    prepared_data = await ProductReplicationPreparer.prepare_filters_to_delete_multiple_products(filters)
    prepared_data = prepared_data.dict()

    if prepared_data["product_ids"] is not None:
        prepared_data["product_ids"] = [str(product_id) for product_id in prepared_data["product_ids"]]

    if prepared_data["parent_ids"] is not None:
        prepared_data["parent_ids"] = [str(parent_id) for parent_id in prepared_data["parent_ids"]]

    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.crud.delete.many', message=prepared_data)


async def replicate_updated_discounts(product_ids: List[ObjectId], discounts: Optional[List[Decimal]]):
    prepared_data = await ProductReplicationPreparer.prepare_data_update_product_discounts(product_ids, discounts)
    prepared_data = prepared_data.dict()

    prepared_data["product_ids"] = [str(product_id) for product_id in prepared_data["product_ids"]]
    if prepared_data["discounts"] is not None:
        prepared_data["discounts"] = [str(discount) for discount in prepared_data["discounts"]]

    producer = Producer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    producer.send_message(routing_key='products.set.discounts', message=prepared_data)
