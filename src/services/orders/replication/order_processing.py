from src.apps.products.replication_schemes.order_processing.product_release import ProductReleaseData
from src.apps.products.replication_schemes.order_processing.product_reservation import ProductReservationData
from src.dependencies.service_dependencies.products import get_product_service


class OrderProcessingHandler:
    @staticmethod
    async def reserve_products_and_remove_cart_items(data: ProductReleaseData) -> None:
        product_service = await get_product_service()
        await product_service.reserve_for_order(data["products"])

    @staticmethod
    async def release_products(data: ProductReservationData) -> None:
        product_service = await get_product_service()
        await product_service.release_from_order(data["products"])
