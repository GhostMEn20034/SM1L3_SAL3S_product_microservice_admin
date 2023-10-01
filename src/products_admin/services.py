from src.database import db
from src.schemes import PyObjectId
from fastapi.exceptions import HTTPException


async def get_facets_and_variation_themes(category_id: PyObjectId):
    category = await db.categories.find_one({"_id": category_id}, {"tree_id": 0, "parent_id": 0})
    if not category:
        raise HTTPException(status_code=404, detail="Category with the specified id doesn't exist")

    facets = await db.facets.find(
        {
            "$or": [
                {"categories": category_id},
                {"categories": "*"}
            ],
            "code": {"$ne": "price"}
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

    facet_types = await db.facet_types.find({"value": {"$ne": "list"}}).to_list(length=None)

    return {
        "facets": facets,
        "variation_themes": variation_themes,
        "facet_types": facet_types,
        "category": category,
    }
