from typing import Any

from .replication.order_processing import OrderProcessingHandler


async def handle_order_processing_messages(routing_key: str, message: Any) -> None:
    base_routing_key = "orders"

    if routing_key == base_routing_key + ".products.reserve_and_remove_cart_items":
        return await OrderProcessingHandler.reserve_products_and_remove_cart_items(message)
    elif routing_key == base_routing_key + ".products.release":
        return await OrderProcessingHandler.release_products(message)
