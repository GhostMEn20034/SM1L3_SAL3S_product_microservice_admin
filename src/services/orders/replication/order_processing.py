from src.apps.products.service import ProductAdminService


class OrderProcessingHandler:
    @staticmethod
    async def reserve_products_and_remove_cart_items(data) -> None:
        print(data)

    @staticmethod
    async def release_products(data):
        print(data)
