import fastapi
import math
from .schemes import FacetFilters, Facet, FacetList, FacetUpdate
from src.schemes import PyObjectId
from .utils import FacetFiltersHandler
from . import services

router = fastapi.APIRouter(
    prefix='/facets',
    tags=["Facets"]
)


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
    modified_document = await services.update_facet(facet_id, data_to_update.dict())
    if modified_document:
        return

    print(data_to_update.dict())

    return fastapi.responses.JSONResponse(status_code=400, content={"error": "Facet wasn't updated"})

