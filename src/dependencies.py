from src.categories_admin.repository import CategoryRepository
from src.categories_admin.service import CategoryService
from src.deals_admin.repository import DealRepository
from src.deals_admin.service import DealAdminService
from src.facet_types.repository import FacetTypeRepository
from src.facet_types.service import FacetTypeService
from src.facets.repository import FacetRepository
from src.facets.service import FacetService
from src.synonyms.repository import SynonymRepository
from src.synonyms.service import SynonymService
from src.variaton_themes.repository import VariationThemeRepository
from src.variaton_themes.services import VariationThemesService
from src.products_admin.repository import ProductAdminRepository
from src.products_admin.service import ProductAdminService
from src.events_admin.repository import EventRepository
from src.events_admin.service import EventAdminService


async def get_category_service() -> CategoryService:
    repository = CategoryRepository()
    return CategoryService(repository)


def get_facet_type_service() -> FacetTypeService:
    repository = FacetTypeRepository()
    return FacetTypeService(repository)


async def get_variation_theme_service() -> VariationThemesService:
    repository = VariationThemeRepository()
    return VariationThemesService(repository)


async def get_product_admin_service() -> ProductAdminService:
    product_repo = ProductAdminRepository()
    category_repo = CategoryRepository()
    facet_repo = FacetRepository()
    variation_theme_repo = VariationThemeRepository()
    facet_type_repo = FacetTypeRepository()
    return ProductAdminService(product_repo, category_repo, facet_repo, variation_theme_repo, facet_type_repo)


async def get_facet_service() -> FacetService:
    product_service = await get_product_admin_service()
    repository = FacetRepository()
    return FacetService(repository, product_service)


async def get_synonym_service() -> SynonymService:
    repository = SynonymRepository()
    return SynonymService(repository)


async def get_event_admin_service() -> EventAdminService:
    repository = EventRepository()
    product_service = await get_product_admin_service()
    return EventAdminService(repository, product_service)

async def get_deal_admin_service() -> DealAdminService:
    deal_repository = DealRepository()
    category_repository = CategoryRepository()
    facet_repository = FacetRepository()
    return DealAdminService(deal_repository, category_repository, facet_repository)
