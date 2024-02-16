from typing import Optional
import fastapi
from fastapi import Depends

from .service import DealAdminService
from .schemes import create, get, update
from src.dependencies import get_deal_admin_service
from src.schemes.py_object_id import PyObjectId

router = fastapi.APIRouter(
    prefix="/admin/deals",
    tags=["Admin-Deals"]
)


@router.get("/", response_model=get.DealListResponse)
async def deal_list(page: int = fastapi.Query(1, ge=1),
                                        page_size: int = fastapi.Query(15, ge=0),
                                        service: DealAdminService = Depends(get_deal_admin_service)):
    """
    Returns the list of categories and count of pages.
    """
    result = await service.get_deals(page, page_size)
    return result


@router.get("/create", response_model=get.DealCreationEssentialsResponse)
async def get_deal_creation_essentials(facet_category: Optional[PyObjectId] = fastapi.Query(None),
                                       service: DealAdminService = Depends(get_deal_admin_service)):
    return await service.get_deal_creation_essentials(facet_category)


@router.post("/create", status_code=fastapi.status.HTTP_201_CREATED)
async def create_deal(created_data: create.CreateDealSchema,
                      service: DealAdminService = Depends(get_deal_admin_service)):
    await service.create_deal(created_data)


@router.get("/{deal_id}", response_model=get.DealDetailResponse)
async def deal_detail(deal_id: PyObjectId, service: DealAdminService = Depends(get_deal_admin_service)):
    result = await service.get_deal_by_id(deal_id)
    return result


@router.put("/{deal_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def update_deal(deal_id: PyObjectId, data_to_update: update.UpdateDealSchema,
                      service: DealAdminService = Depends(get_deal_admin_service)):
    await service.update_deal(deal_id, data_to_update)


@router.delete("/{deal_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_deal(deal_id: PyObjectId, service: DealAdminService = Depends(get_deal_admin_service)):
    await service.delete_deal(deal_id)
