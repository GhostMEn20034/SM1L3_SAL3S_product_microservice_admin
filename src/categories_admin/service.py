from math import ceil
from typing import Union, Tuple, Optional
from fastapi.exceptions import HTTPException
from bson import ObjectId
from .utils import CategoryTree
from .repository import CategoryRepository


class CategoryService:
    """
    Delegate calls to the repository, adding business logic or validation if needed
    """
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def form_category_attrs(self, parent_id: Union[ObjectId, None]) -> Tuple[dict, Optional[str]]:
        """
            Returns parent_id, tree_id, level for the category that will be inserted or updated.
            If parent does not exist, function return empty dict and string with error message
            :param parent_id: ID of the parent category, if you pass parent ID which not eq to None,
            make sure that parent exists
        """
        # parent_id means that category will be root node.
        # So function will return generated tree_id, zero level, and parent_id None
        if parent_id is None:
            category_attrs = {
                "level": 0,
                "tree_id": ObjectId(),
                "parent_id": None
            }
            return category_attrs, None

        parent = await self.repository.get_one_category({"_id": parent_id}, {"level": 1, "tree_id": 1})

        if not parent: return {}, "not_found"

        # If everything is fine return level equals to the parent level + 1,
        # tree_id of the parent, parent_id equals to _id of parent
        category_attrs = {
            "level": parent["level"] + 1,
            "tree_id": parent["tree_id"],
            "parent_id": parent_id
        }
        return category_attrs, None

    async def get_categories_for_choices(self):
        return await self.repository.get_category_list({}, {"name": 1, "groups": 1})

    async def get_categories_for_admin_panel(self, page: int, page_size: int):
        categories = await self.repository.get_categories_with_document_count(page, page_size)
        if not categories.get("result"):
            result = {
                "result": [],
                "page_count": 1,
            }
            return result

        category_count = categories.get("total_count").get("total")

        result = {
            "result": categories.get("result"),
            "page_count": ceil(category_count / page_size), # Calculating count of pages
        }

        return result

    async def get_category_by_id(self, category_id: ObjectId):
        # Retrieve a category with the specified ID
        category = await self.repository.get_one_category({"_id": category_id})
        # If there's no category, raise HTTP 404
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        # Otherwise return category
        return category

    async def get_categories_tree(self):
        """
        Returns categories in a tree-like format
        """
        category_list = await self.repository.get_category_list({}, {"groups": 0})
        category_tree = CategoryTree(category_list)
        # Return categories as tree
        return category_tree.get_whole_tree()

    async def update_category(self, category_id: ObjectId, data_to_update: dict):
        # Query a category with _id equal to category_id
        category = await self.repository.get_one_category({"_id": category_id},
                                                          {"parent_id": 1, "level": 1})
        # if there's no category with the specified id return HTTP 404 Not Found
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        # get ID of parent
        parent_id = data_to_update.pop("parent_id")
        # if category is root node and user tries to change parent_id
        # raise an error that parent cannot be changed in the root node
        if category["level"] == 0 and category["parent_id"] != parent_id:
            raise HTTPException(status_code=400, detail="You cannot change parent of root node")
        # if user tries to change category parent
        # then parent_id, tree_id and level will be changed in the category
        if category["parent_id"] != parent_id:
            # get level, tree_id, parent_id
            category_attrs, err = await self.form_category_attrs(parent_id)
            # If parent does not exist, raise HTTP 404
            if err == "not_found":
                raise HTTPException(status_code=404, detail="Parent not found")
            # set new data to update
            new_category_data = {**data_to_update, **category_attrs}
        else:
            # if new parent was not specified, keep data to update in the same state
            new_category_data = {**data_to_update}

        await self.repository.update_category({"_id": category_id}, {"$set": new_category_data})

    async def create_category(self, data: dict):
        # get the parent ID
        parent_id = data.pop("parent_id")
        # get level, tree_id, parent_id
        category_attrs, err = await self.form_category_attrs(parent_id)
        # If parent does not exist, raise HTTP 404
        if err == "not_found":
            raise HTTPException(status_code=404, detail="Parent not found")
        # insert category
        created_category = await self.repository.create_category({**data, **category_attrs})
        # if category was not created, then raise HTTP 404
        if not created_category:
            raise HTTPException(status_code=400, detail="Category not created")

    async def delete_category(self, category_id: ObjectId):
        # Trying to find a category that user wants to delete
        category = await self.repository.get_one_category({"_id": category_id}, {"_id": 1})
        # if category wasn't found raise HTTP 404 Not Found
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        # Trying to find category children
        children = await self.repository.get_category_list({"parent_id": category["_id"]}, {"_id": 1})
        # if there are children, then raise HTTP 400
        if children:
            raise HTTPException(status_code=400,
                                detail="Before deleting a category, make sure that the category has no children")

        # Delete a category if everything is fine
        await self.repository.delete_category({"_id": category_id})
