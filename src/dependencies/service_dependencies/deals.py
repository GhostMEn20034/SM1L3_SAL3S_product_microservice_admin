from src.apps.categories.repository import CategoryRepository
from src.apps.deals.repository import DealRepository
from src.apps.deals.service import DealAdminService
from src.apps.facets.repository import FacetRepository


async def get_deal_service() -> DealAdminService:
    deal_repository = DealRepository()
    category_repository = CategoryRepository()
    facet_repository = FacetRepository()
    return DealAdminService(deal_repository, category_repository, facet_repository)