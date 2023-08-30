import fastapi
import math
from .schemes import (
    FacetFilters,
    Facet,
    FacetList,
    FacetUpdate,
    FacetCreate
)
from src.schemes import PyObjectId
from .utils import FacetFiltersHandler
from . import services

router = fastapi.APIRouter(
    prefix='/facets',
    tags=["Facets"]
)

@router.get("/for-choices")
async def facet_list_for_choices():
    facets = await services.get_facets_for_choices()
    return facets

@router.get("/", response_model=FacetList, response_model_exclude_none=True)
async def facet_list(filters: FacetFilters = fastapi.Depends(FacetFilters), page: int = fastapi.Query(1, ge=1),
                     page_size: int = fastapi.Query(15, ge=0)):
    """
    Returns list of facets
    """
    filter_handler = FacetFiltersHandler(filters.dict(exclude_none=True))
    generated_filters = filter_handler.generate_filters()

    facets = await services.get_facets(generated_filters, page, page_size)

    page_count = facets[0].get("total_count")[0].get("total")

    result = {
        "result": facets[0].get("result"),
        "page_count": math.ceil(page_count / page_size)
    }
    return result


@router.get("/{facet_id}", response_model=Facet, response_model_exclude_none=True)
async def facet_detail(facet_id: PyObjectId):
    """Returns facet with specified id"""
    facet = await services.get_facet_by_id(facet_id)

    if not facet:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="Facet not found")

    return facet


@router.put("/{facet_id}")
async def facet_update(facet_id: PyObjectId, data_to_update: FacetUpdate):
    """Updates facet"""
    await services.update_facet(facet_id, data_to_update.dict())


@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def facet_create(data: FacetCreate):
    """Create facet with data specified by the user"""
    await services.create_facet(data.dict())


@router.delete("/{facet_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def facet_delete(facet_id: PyObjectId):
    await services.delete_facet(facet_id)
