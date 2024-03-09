import fastapi
from fastapi import Depends

from src.dependencies.service_dependencies.search_terms import get_search_terms_service
from .service import SearchTermsAdminService
from .schemes import get
from .schemes import create
from .schemes import update
from .schemes import delete
from src.schemes.py_object_id import PyObjectId
from src.dependencies.user_dependencies import is_staff_user

router = fastapi.APIRouter(
    prefix="/admin/search-terms",
    tags=["Admin-Search-Terms"],
    dependencies=[Depends(is_staff_user)]
)


@router.get("/", response_model=get.SearchTermsListResponse)
async def get_search_terms_list(filters: get.SearchTermsFilters = Depends(get.SearchTermsFilters),
                                service: SearchTermsAdminService = Depends(get_search_terms_service)):
    return await service.search_terms_list(filters.page, filters.page_size, filters.name)


@router.get("/{search_term_id}", response_model=get.SearchTermDetailResponse)
async def search_term_detail(search_term_id: PyObjectId,
                             service: SearchTermsAdminService = Depends(get_search_terms_service)):
    search_term = await service.get_search_term_by_id(search_term_id)
    return {'search_term': search_term}


@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def create_search_term(data_to_insert: create.CreateSearchTerm,
                             service: SearchTermsAdminService = Depends(get_search_terms_service)):
    await service.create_search_term(data_to_insert)


@router.put("/{search_term_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def update_search_term(search_term_id: PyObjectId, data_to_update: update.UpdateSearchTerm,
                             service: SearchTermsAdminService = Depends(get_search_terms_service)):
    await service.update_search_term(search_term_id, data_to_update)


@router.delete("/{search_term_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_search_term(search_term_id: PyObjectId,
                             service: SearchTermsAdminService = Depends(get_search_terms_service)):
    await service.delete_search_term(search_term_id)


@router.delete("/", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_many_search_terms(delete_data: delete.DeleteSearchTermsRequest = fastapi.Body(...),
                                   service: SearchTermsAdminService = Depends(get_search_terms_service)):
    await service.delete_many_search_terms(delete_data.search_terms_ids)
