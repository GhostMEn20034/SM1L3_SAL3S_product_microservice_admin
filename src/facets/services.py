from src.database import db
from src.schemes import PyObjectId

async def get_facets(filters: dict, page: int, page_size: int):
    pipeline = [
        {
            "$match": {
                **filters
            }
        },
        {
            "$facet": {
                "result": [
                    {
                        "$project": {
                            "values": 0,
                            "categories": 0
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

    facets = await db.facets.aggregate(pipeline).to_list(length=None)
    return facets


async def get_facet_by_id(facet_id):
    facet = await db.facets.find_one({"_id": facet_id})
    return facet


async def update_facet(facet_id: PyObjectId, data_to_update: dict):
    await db.facets.update_one({"_id": facet_id},{"$set": data_to_update})


async def create_facet(data: dict):
    await db.facets.insert_one(data)

async def delete_facet(facet_id: PyObjectId):
    await db.facets.delete_one({"_id": facet_id})
