from decimal import Decimal
from typing import List, Dict
from bson import ObjectId

from src.param_classes.products.attach_to_event_params import AttachToEventParams
from src.param_classes.products.detach_from_event_params import DetachFromEventParams
from .product_replication_preparer import ProductReplicationPreparer
from src.core.message_broker.async_producer import AsyncProducer
from src.utils import convert_type
from src.config.settings import PRODUCT_CRUD_EXCHANGE_TOPIC_NAME


async def connect_async_producer_to_broker(async_producer: AsyncProducer):
    await async_producer.connect()

async def replicate_single_created_product(product_data: Dict):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_created_single_product(product_data)
    prepared_data = prepared_data.dict()
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    convert_type(prepared_data, ObjectId, str)
    convert_type(prepared_data, Decimal, str)

    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.crud.create.one', message=prepared_data)


async def replicate_created_variations(variations: List[Dict]):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_created_variations(variations)
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    prepared_data = [convert_type(variation.dict(), ObjectId, str) for variation in prepared_data]
    prepared_data = [convert_type(variation, Decimal, str) for variation in prepared_data]

    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.crud.create.many', message=prepared_data)


async def replicate_single_updated_product(product_data: Dict):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_updated_single_product(product_data)
    prepared_data = prepared_data.dict()
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    convert_type(prepared_data, ObjectId, str)
    convert_type(prepared_data, Decimal, str)

    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.crud.update.one', message=prepared_data)


async def replicate_updated_variations(variations: List[Dict]):
    prepared_data = await ProductReplicationPreparer.prepare_data_of_updated_variations(variations)
    # convert Decimal and ObjectId to string, since these types are not serializable in rabbitmq
    prepared_data = [convert_type(variation.dict(), ObjectId, str) for variation in prepared_data]
    prepared_data = [convert_type(variation, Decimal, str) for variation in prepared_data]

    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.crud.update.many', message=prepared_data)


async def replicate_single_product_delete(product_id: ObjectId):
    prepared_data = await ProductReplicationPreparer.prepare_filters_to_delete_single_product(product_id)
    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.crud.delete.one', message={"_id": str(prepared_data)})


async def replicate_variations_delete(filters: dict):
    prepared_data = await ProductReplicationPreparer.prepare_filters_to_delete_multiple_products(filters)
    prepared_data = prepared_data.dict()

    if prepared_data["product_ids"] is not None:
        prepared_data["product_ids"] = [str(product_id) for product_id in prepared_data["product_ids"]]

    if prepared_data["parent_ids"] is not None:
        prepared_data["parent_ids"] = [str(parent_id) for parent_id in prepared_data["parent_ids"]]

    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.crud.delete.many', message=prepared_data)

async def replicate_product_attachment_to_event(params: AttachToEventParams):
    prepared_data = await ProductReplicationPreparer.prepare_data_update_product_discounts(params)
    prepared_data = prepared_data.dict()

    prepared_data["product_ids"] = [str(product_id) for product_id in prepared_data["product_ids"]]
    prepared_data["discounts"] = [str(discount) for discount in prepared_data["discounts"]]
    prepared_data["event_id"] = str(prepared_data["event_id"])

    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.attach_to_event', message=prepared_data)

async def replicate_product_detachment_from_event(params: DetachFromEventParams):
    prepared_data = {
        "event_id": str(params.event_id),
    }
    producer = AsyncProducer(exchange_name=PRODUCT_CRUD_EXCHANGE_TOPIC_NAME, exchange_type='topic')
    await connect_async_producer_to_broker(producer)
    await producer.send_message(routing_key='products.detach_from_event', message=prepared_data)
