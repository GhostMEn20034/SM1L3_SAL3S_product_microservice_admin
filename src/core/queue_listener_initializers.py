import aio_pika
from aio_pika import ExchangeType

from src.logger import logger
from src.config import settings
from src.core.message_broker.async_consumer import AsyncConsumer
from src.services.orders.message_handler import handle_order_processing_messages

async def initialize_order_processing_listener() -> AsyncConsumer:
    binding_key = 'orders.products.#'
    exchange_name = settings.ORDER_PROCESSING_EXCHANGE_TOPIC_NAME
    consumer = AsyncConsumer(exchange_name=exchange_name, exchange_type=ExchangeType.TOPIC)

    await consumer.connect(settings.AMPQ_CONNECTION_URL)
    await consumer.bind_queue(binding_key)

    # Start consuming messages
    async def callback(message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process():
            logger.info(f"Received message: {message.body} ---- routing key: {message.routing_key}")
            await handle_order_processing_messages(message.routing_key, message.body)

    await consumer.consume(callback)
    logger.info("Started Order Processing Consumer")
    return consumer

