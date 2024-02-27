import fastapi
from fastapi import Depends
from .schemes import (
    FacetFilters,
    Facet,
    FacetList,
    FacetUpdate,
    FacetCreate
)
from src.schemes.py_object_id import PyObjectId
from .utils import FacetFiltersHandler
from .service import FacetService
from src.dependencies.service_dependencies.facets import get_facet_service
from src.dependencies.user_dependencies import is_staff_user

router = fastapi.APIRouter(
    prefix='/admin/facets',
    tags=["Facets"],
    dependencies=[Depends(is_staff_user)]
)


@router.get("/for-choices")
async def facet_list_for_choices(service: FacetService = Depends(get_facet_service)):
    """
    Returns a list of facets that can be used in forms where user can choose options
    """
    facets = await service.get_facets_for_choices()
    return facets


@router.get("/", response_model=FacetList, response_model_exclude_none=True)
async def facet_list(filters: FacetFilters = fastapi.Depends(FacetFilters), page: int = fastapi.Query(1, ge=1, ),
                     page_size: int = fastapi.Query(15, ge=0),
                     service: FacetService = Depends(get_facet_service)):
    """
    Returns list of facets
    """
    filter_handler = FacetFiltersHandler(filters.dict(exclude_none=True))
    generated_filters = filter_handler.generate_filters()
    result = await service.get_facets(generated_filters, page, page_size)
    return result


@router.get("/{facet_id}", response_model=Facet)
async def facet_detail(facet_id: PyObjectId, service: FacetService = Depends(get_facet_service)):
    """Returns facet with specified id"""
    facet = await service.get_facet_by_id(facet_id)
    return facet


@router.put("/{facet_id}")
async def facet_update(facet_id: PyObjectId, data_to_update: FacetUpdate,
                       service: FacetService = Depends(get_facet_service)):
    """Updates facet"""
    await service.update_facet(facet_id, data_to_update.dict())


@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def facet_create(data: FacetCreate, service: FacetService = Depends(get_facet_service)):
    """Create facet with data specified by the user"""
    await service.create_facet(data.dict())


@router.delete("/{facet_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def facet_delete(facet_id: PyObjectId, service: FacetService = Depends(get_facet_service)):
    """Deletes facet"""
    await service.delete_facet(facet_id=facet_id)
