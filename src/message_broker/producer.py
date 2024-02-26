import json
from typing import Any
from pika import URLParameters, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from src.config.settings import AMPQ_CONNECTION_URL

class Producer:
    """
    Class responsible for sending messages to the broker
    """
    def __init__(self, exchange_name: str, exchange_type: str):
        self._exchange_name: str = exchange_name

        self._parameters: URLParameters = URLParameters(AMPQ_CONNECTION_URL)
        self._connection: BlockingConnection = BlockingConnection(parameters=self._parameters)

        self._channel: BlockingChannel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange_name, exchange_type=exchange_type)

    def send_message(self, routing_key: str, message: Any) -> None:
        message_body = json.dumps(message)
        self._channel.basic_publish(exchange=self._exchange_name, routing_key=routing_key, body=message_body)

    def close(self) -> None:
        self._connection.close()
