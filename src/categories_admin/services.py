from src.database import db
from bson.objectid import ObjectId
from src.schemes import PyObjectId
from typing import Union
from fastapi.exceptions import HTTPException
from .utils import CategoryTree

async def get_categories_for_choices():
    categories = await db.categories.find({}, {"name": 1, "groups": 1}).to_list(length=None)
    return categories


async def get_categories_for_admin_panel(page: int, page_size: int):
    """
    Returns specified number of categories and total category count,
    :param page_size - number of categories to return
    :param page - page number.
    """
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
    """
    Returns parent_id, tree_id, level for the category that will be inserted or updated
    """

    # parent_id means that category will be root node.
    # So function will return generated tree_id, zero level, and parent_id None
    if parent_id is None:
        category_attrs = {
            "level": 0,
            "tree_id": ObjectId(),
            "parent_id": None
        }
        return category_attrs

    parent = await db.categories.find_one({"_id": parent_id}, {"level": 1, "tree_id": 1})

    # if user passes some parent_id and
    # there's no parent category with _id equals to the parent_id,
    # then function will raise HTTP 404 Not Found
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    # If everything is fine return level equals to the parent level + 1,
    # tree_id of the parent, parent_id equals to _id of parent
    category_attrs = {
        "level": parent["level"] + 1,
        "tree_id": parent["tree_id"],
        "parent_id": parent_id
    }
    return category_attrs


async def update_category(category_id: PyObjectId, data_to_update: dict):
    # Query a category with _id equal to category_id
    category = await db.categories.find_one({"_id": category_id}, {"parent_id": 1, "level": 1})

    # if there's no category with the specified id return HTTP 404 Not Found
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    parent_id = data_to_update.pop("parent_id")

    # if category is root node and user tries to change parent_id
    # raise an error that parent cannot be changed in the root node
    if category["level"] == 0 and category["parent_id"] != parent_id:
        raise HTTPException(status_code=400, detail="You cannot change parent of root node")

    # if user tries to change category parent
    # then parent_id, tree_id and level will be changed in the category
    if category["parent_id"] != parent_id:
        category_attrs = await form_category_attrs(parent_id)
        new_category_data = {**data_to_update, **category_attrs}
    else:
        new_category_data = {**data_to_update}

    await db.categories.update_one({"_id": category_id}, {"$set": new_category_data})


async def create_category(data: dict):
    parent_id = data.pop("parent_id")

    # get level, tree_id, parent_id
    category_attrs = await form_category_attrs(parent_id)

    # insert category
    created_category = await db.categories.insert_one({**data, **category_attrs})

    # if category was not inserted, then return False, otherwise return True
    if not created_category.inserted_id:
        return False

    return True


async def delete_category(category_id: PyObjectId):
    # Trying to find a category that user wants to delete
    category = await db.categories.find_one({"_id": category_id}, {"_id": 1})

    # if category wasn't found raise HTTP 404 Not Found
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Trying to find category children
    children = await db.categories.find({"parent_id": category["_id"]}, {"_id": 1}).to_list(length=None)

    # if there are children, then raise HTTP 400
    if children:
        raise HTTPException(status_code=400,
                            detail="Before deleting a category, make sure that the category has no children")

    # Delete a category if everything is fine
    await db.categories.delete_one({"_id": category["_id"]})



async def get_categories_tree():
    """
    Returns categories in a tree-like format
    """
    category_list = await db.categories.find({}, {"groups": 0}).to_list(length=None)

    category_tree = CategoryTree(category_list)

    # Return categories as tree
    return category_tree.get_whole_tree()
