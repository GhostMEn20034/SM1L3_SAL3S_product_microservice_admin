from src.database import db
from bson.objectid import ObjectId
from src.schemes import PyObjectId
from typing import Union
from fastapi.exceptions import HTTPException


async def get_categories_for_choices():
    categories = await db.categories.find({}, {"name": 1}).to_list(length=None)
    return categories


async def get_categories_for_admin_panel(page: int, page_size: int):
    pipeline = [
        {
            "$facet": {
                "result": [
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

    categories = await db.categories.aggregate(pipeline).to_list(length=None)
    return categories


async def get_category_by_id(category_id: PyObjectId):
    category = await db.categories.find_one({"_id": category_id})
    return category


async def form_category_attrs(parent_id: Union[PyObjectId, None]):
    if parent_id is None:
        category_attrs = {
            "level": 0,
            "tree_id": ObjectId(),
            "parent_id": None
        }
        return category_attrs

    parent = await db.categories.find_one({"_id": parent_id}, {"level": 1, "tree_id": 1})

    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    category_attrs = {
        "level": parent["level"] + 1,
        "tree_id": parent["tree_id"],
        "parent_id": parent_id
    }
    return category_attrs


async def update_category(category_id: PyObjectId, data_to_update: dict):
    category = await db.categories.find_one({"_id": category_id}, {"parent_id": 1, "level": 1})

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    parent_id = data_to_update.pop("parent_id")

    if category["level"] == 0 and category["parent_id"] != parent_id:
        raise HTTPException(status_code=400, detail="You cannot change parent of root node")

    if category["parent_id"] != parent_id:
        category_attrs = await form_category_attrs(parent_id)
        new_category_data = {**data_to_update, **category_attrs}
    else:
        new_category_data = {**data_to_update}

    await db.categories.update_one({"_id": category_id}, {"$set": new_category_data})


async def create_category(data: dict):
    parent_id = data.pop("parent_id")

    category_attrs = await form_category_attrs(parent_id)

    created_category = await db.categories.insert_one({**data, **category_attrs})

    if not created_category.inserted_id:
        return False

    return True


async def delete_category(category_id: PyObjectId):
    category = await db.categories.find_one({"_id": category_id}, {"_id": 1})

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    children = await db.categories.find({"parent_id": category["_id"]}, {"_id": 1}).to_list(length=None)

    if children:
        raise HTTPException(status_code=400,
                            detail="Before deleting a category, make sure that the category has no children")

    await db.categories.delete_one({"_id": category["_id"]})
