import json
import threading
import logging

from src.core.message_broker.consumer import Consumer


class BaseQueueListener(threading.Thread):
    BINDING_KEY = None
    exchange_name = None
    message_handler_func = None
    exchange_type = "topic"

    def __init__(self):
        super().__init__()

        # Check if BINDING_KEY, exchange_name, and message_handler_func are defined in the subclass
        if self.BINDING_KEY is None:
            raise ValueError("BINDING_KEY must be defined in the subclass")
        if self.exchange_name is None:
            raise ValueError("exchange_name must be defined in the subclass")
        if self.message_handler_func is None or not callable(self.message_handler_func):
            raise ValueError("message_handler_func must be defined and callable in the subclass")

        self.consumer = Consumer(
            exchange_name=self.exchange_name,
            exchange_type=self.exchange_type
        )
        self.consumer.bind_queue(self.BINDING_KEY)

    def callback(self, _ch, method, _properties, body):
        print(f"[x] {method.routing_key}, {json.loads(body)}")
        self.message_handler_func(method.routing_key, json.loads(body))

    def run(self):
        logging.info('Listener was launched')
        self.consumer.consume(callback=self.callback)
