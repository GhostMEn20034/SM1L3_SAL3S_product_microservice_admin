from src.apps.facets.repository import FacetRepository
from src.apps.facets.service import FacetService
from .products_admin import get_product_admin_service


async def get_facet_service() -> FacetService:
    product_service = await get_product_admin_service()
    repository = FacetRepository()
    return FacetService(repository, product_service)