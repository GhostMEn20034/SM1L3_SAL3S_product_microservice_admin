from asgiref.sync import async_to_sync

from src.config import settings

from .base_queue_listener import BaseQueueListener
from src.services.orders.message_handler import handle_order_processing_messages
from src.utils import async_worker


class OrderProcessingQueueListener(BaseQueueListener):
    BINDING_KEY = 'orders.products.#'
    exchange_name = settings.ORDER_PROCESSING_EXCHANGE_TOPIC_NAME
    message_handler_func = staticmethod(async_to_sync(handle_order_processing_messages))

    def __init__(self):
        super().__init__()

