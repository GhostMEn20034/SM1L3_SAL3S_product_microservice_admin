from src.apps.categories_admin.repository import CategoryRepository
from src.apps.deals_admin.repository import DealRepository
from src.apps.deals_admin.service import DealAdminService
from src.apps.facets.repository import FacetRepository


async def get_deal_admin_service() -> DealAdminService:
    deal_repository = DealRepository()
    category_repository = CategoryRepository()
    facet_repository = FacetRepository()
    return DealAdminService(deal_repository, category_repository, facet_repository)