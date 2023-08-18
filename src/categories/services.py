from src.database import db


async def get_categories():
    categories = await db.categories.find().to_list(length=None)
    return categories
