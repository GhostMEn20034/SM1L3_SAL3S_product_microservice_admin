from src.database import db, client


async def create_product(validated_data: dict):
    products = db.products
    async with await client.start_session() as session:
        async with session.start_transaction():
            product_data = validated_data.get("product_data")
            product_id = await products.insert_one(product_data).inserted_id
