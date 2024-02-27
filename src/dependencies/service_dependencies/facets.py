from src.apps.facets.repository import FacetRepository
from src.apps.facets.service import FacetService
from .products import get_product_service


async def get_facet_service() -> FacetService:
    product_service = await get_product_service()
    repository = FacetRepository()
    return FacetService(repository, product_service)