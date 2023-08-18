from src.database import db


async def get_facet_types():
    facet_types = await db.facet_types.find().to_list(length=None)
    return facet_types
