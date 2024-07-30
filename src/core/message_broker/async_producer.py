import json
from typing import Any
import aio_pika
from aio_pika import ExchangeType
from src.config.settings import AMPQ_CONNECTION_URL

class AsyncProducer:
    """
    Class responsible for sending messages to the broker
    """
    def __init__(self, exchange_name: str, exchange_type: str):
        self._exchange_name: str = exchange_name
        self._exchange_type: ExchangeType = ExchangeType(exchange_type)
        self._connection = None
        self._channel= None
        self._exchange = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(AMPQ_CONNECTION_URL)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(self._exchange_name, self._exchange_type)

    async def send_message(self, routing_key: str, message: Any) -> None:
        message_body = json.dumps(message)
        await self._exchange.publish(
            aio_pika.Message(body=message_body.encode()),
            routing_key=routing_key
        )

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()