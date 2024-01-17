import fastapi
from fastapi import Depends
from typing import List

from src.dependencies import get_facet_type_service
from .service import FacetTypeService
from .schemes import FacetType


router = fastapi.APIRouter(
    prefix='/admin/facet-types',
    tags=["Facet types"]
)


@router.get("/", response_model=List[FacetType])
async def facet_types_list(service: FacetTypeService = Depends(get_facet_type_service)):
    facet_types = await service.get_facet_types()
    return facet_types
