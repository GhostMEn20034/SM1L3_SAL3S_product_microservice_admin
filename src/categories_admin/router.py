import fastapi
import math
from typing import List
from . import services
from . import schemes

from src.schemes import PyObjectId

router = fastapi.APIRouter(
    prefix="/admin/categories",
    tags=["Admin-Categories"]
)


@router.get("/for-choices", response_model=List[schemes.CategoryForChoices])
async def category_list_for_choices():
    """
    Returns the list of categories for choices.
    Used for the forms where choose category required.
    """
    categories = await services.get_categories_for_choices()
    return categories


@router.get("/", response_model=schemes.CategoryAdminPanelList)
async def category_list_for_admin_panel(page: int = fastapi.Query(1, ge=1),
                     page_size: int = fastapi.Query(15, ge=0)):
    """
    Returns the list of categories and count of pages.
    """
    categories = await services.get_categories_for_admin_panel(page, page_size)

    page_count = categories[0].get("total_count")[0].get("total")

    result = {
        "result": categories[0].get("result"),
        "page_count": math.ceil(page_count / page_size)
    }

    return result


@router.get("/tree", response_model=List[schemes.CategoryList])
async def category_list_tree():
    """
    Returns a category list in the tree-like format
    """
    categories = await services.get_categories_tree()
    return categories


@router.get("/{category_id}", response_model=schemes.Category)
async def category_detail(category_id: PyObjectId):
    category = await services.get_category_by_id(category_id)

    if not category:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="Category not found")

    return category


@router.put("/{category_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def category_update(category_id: PyObjectId, data: schemes.CategoryUpdate):
    await services.update_category(category_id, data.dict())


@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def category_create(data: schemes.CategoryCreate):
    created_category = await services.create_category(data.dict())
    if not created_category:
        raise fastapi.exceptions.HTTPException(status_code=400, detail="Category not created")


@router.delete("/{category_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def category_delete(category_id: PyObjectId):
    await services.delete_category(category_id)
