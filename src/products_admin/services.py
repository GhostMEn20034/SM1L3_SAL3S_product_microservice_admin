from src.database import db
from src.schemes import PyObjectId


async def get_facets_and_variation_themes(category_id: PyObjectId):
    facets = await db.facets.find(
        {
            "$or": [
                {"categories": category_id},
                {"categories": "*"}
            ]
        },
        {
            "categories": 0
        }
    ).to_list(length=None)

    variation_themes = await db.variation_themes.find(
        {
            "$or": [
                {"categories": category_id},
                {"categories": "*"}
            ]
        },
        {
            "categories": 0
        }
    ).to_list(length=None)

    return {
        "facets": facets,
        "variation_themes": variation_themes
    }
