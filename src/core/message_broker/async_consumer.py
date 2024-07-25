from typing import Callable

import aio_pika
from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage

from src.logger import logger


class AsyncConsumer:
    """
    Class responsible for getting messages from the broker
    """
    def __init__(self, exchange_name: str, exchange_type: str):
        self._exchange_name: str = exchange_name
        self._exchange_type: ExchangeType = ExchangeType(exchange_type)
        self._connection = None
        self._channel = None
        self._exchange = None
        self._queue = None
        self._queue_name = None

    async def connect(self, connection_string: str):
        self._connection = await aio_pika.connect_robust(connection_string)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(self._exchange_name, self._exchange_type)

        self._queue = await self._channel.declare_queue('', exclusive=True)
        self._queue_name: str = self._queue.name

    async def bind_queue(self, binding_key: str):
        await self._queue.bind(self._exchange, routing_key=binding_key)

    async def consume(self, callback: Callable):
        async def on_message(message: AbstractIncomingMessage):
            await callback(message)

        await self._queue.consume(on_message)

    async def close(self):
        await self._channel.close()
        await self._connection.close()
        logger.info("Message consumer closed successfully")