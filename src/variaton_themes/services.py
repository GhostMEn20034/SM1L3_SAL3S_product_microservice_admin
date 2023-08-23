from src.database import db
from src.schemes import PyObjectId

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
