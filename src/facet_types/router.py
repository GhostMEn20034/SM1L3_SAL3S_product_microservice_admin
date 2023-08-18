import fastapi
from .services import get_facet_types
from .schemes import FacetType
from typing import List

router = fastapi.APIRouter(
    prefix='/facet-types',
    tags=["Facet types"]
)


@router.get("/", response_model=List[FacetType])
async def facet_types_list():
    facet_types = await get_facet_types()
    return facet_types
