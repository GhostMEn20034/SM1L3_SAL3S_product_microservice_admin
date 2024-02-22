import fastapi
from typing import List
from fastapi import Depends
from .service import CategoryService
from . import schemes
from src.dependencies.service_dependencies.categories import get_category_service
from src.schemes.py_object_id import PyObjectId

router = fastapi.APIRouter(
    prefix="/admin/categories",
    tags=["Admin-Categories"]
)


@router.get("/for-choices", response_model=List[schemes.CategoryForChoices])
async def category_list_for_choices(service: CategoryService = Depends(get_category_service)):
    """
    Returns the list of categories for choices.
    Used for the forms where choose category required.
    """
    categories = await service.get_categories_for_choices()
    return categories

@router.get("/", response_model=schemes.CategoryAdminPanelListResponse)
async def category_list_for_admin_panel(page: int = fastapi.Query(1, ge=1),
                                        page_size: int = fastapi.Query(15, ge=0),
                                        service: CategoryService = Depends(get_category_service)):
    """
    Returns the list of categories and count of pages.
    """
    result = await service.get_categories_for_admin_panel(page, page_size)
    return result

@router.get("/tree", response_model=List[schemes.CategoryList])
async def category_list_tree(service: CategoryService = Depends(get_category_service)):
    """
    Returns a category list in the tree-like format
    """
    result = await service.get_categories_tree()
    return result

@router.get("/{category_id}", response_model=schemes.Category)
async def category_detail(category_id: PyObjectId, service: CategoryService = Depends(get_category_service)):
    result = await service.get_category_by_id(category_id)
    return result

@router.put("/{category_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def category_update(category_id: PyObjectId,
                          data: schemes.CategoryUpdate,
                          service: CategoryService = Depends(get_category_service)):
    await service.update_category(category_id, data.dict())

@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def category_create(data: schemes.CategoryCreate, service: CategoryService = Depends(get_category_service)):
    await service.create_category(data.dict())

@router.delete("/{category_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def category_delete(category_id: PyObjectId, service: CategoryService = Depends(get_category_service)):
    await service.delete_category(category_id)
