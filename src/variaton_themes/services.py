from src.database import db
from src.schemes import PyObjectId
from fastapi.exceptions import HTTPException

async def get_variation_themes(page: int, page_size: int):
    pipeline = [
        {
            "$facet": {
                "result": [
                    {
                        "$project": {
                            "_id": 1,
                            "name": 1
                        }
                    },
                    {
                        "$skip": (page - 1) * page_size
                    },
                    {
                        "$limit": page_size
                    }
                ],
                "total_count": [
                    {"$count": "total"}
                ]
            }
        },
    ]

    variation_themes = await db.variation_themes.aggregate(pipeline).to_list(length=None)
    return variation_themes


async def get_variation_theme_by_id(variation_theme_id: PyObjectId):
    variation_theme = await db.variation_themes.find_one({"_id": variation_theme_id})
    return variation_theme


async def update_variation_theme(variation_theme_id: PyObjectId, data: dict):
    variation_theme = await db.variation_themes.find_one({"_id": variation_theme_id}, {"_id": 1})
    if not variation_theme:
        raise HTTPException(status_code=404, detail="Variation theme not found")

    await db.variation_themes.update_one({"_id": variation_theme_id}, {"$set": data})


async def create_variation_theme(data: dict):
    created_variation_theme = await db.variation_themes.insert_one(data)
    if created_variation_theme.inserted_id:
        return True

    return False


async def delete_variation_theme(variation_theme_id: PyObjectId):
    variation_theme = await db.variation_themes.find_one({"_id": variation_theme_id}, {"_id": 1})
    if variation_theme:
        raise HTTPException(status_code=404, detail="Variation theme not found")

    await db.variation_themes.delete_one({"_id": variation_theme_id})
