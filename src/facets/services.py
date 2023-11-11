from src.database import db
from src.schemes import PyObjectId
from fastapi.exceptions import HTTPException


async def get_facets_for_choices():
    facets = await db.facets.find({ }, {"name": 1, "code": 1, "_id": 0}).to_list(length=None)
    return facets

async def get_facets(filters: dict, page: int, page_size: int):
    """
    Returns specified number of facets and total facet count,
    :param filters - dict with parameters used to filter facets
    :param page - page number
    :param page_size - number of facets to return
    """
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
    """
    Updates facet with specified id,
    :param facet_id - facet identifier,
    :param data_to_update - new facet properties.
    """
    facet = await db.facets.find_one({"_id": facet_id}, {"_id": 1})
    # if there's no facet with the specified id raise HTTP 404 Not Found
    if not facet:
        raise HTTPException(status_code=404, detail="Facet not found")

    # Update facet
    await db.facets.update_one({"_id": facet_id},{"$set": data_to_update})


async def create_facet(data: dict):
    created_facet = await db.facets.insert_one(data)
    if created_facet.inserted_id:
        return True

    return False

async def delete_facet(facet_id: PyObjectId):
    """
    Deletes facet with specified id
    """
    facet = await db.facets.find_one({"_id": facet_id}, {"_id": 1})
    # if there's no facet with such id, raise HTTP 404 Not Found
    if not facet:
        raise HTTPException(status_code=404, detail="Facet not found")

    # If facet was found, then delete facet
    await db.facets.delete_one({"_id": facet_id})
