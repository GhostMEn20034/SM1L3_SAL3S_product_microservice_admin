from src.categories_admin.repository import CategoryRepository
from src.categories_admin.service import CategoryService
from src.facet_types.repository import FacetTypeRepository
from src.facet_types.service import FacetTypeService
from src.facets.repository import FacetRepository
from src.facets.service import FacetService
from src.variaton_themes.repository import VariationThemeRepository
from src.variaton_themes.services import VariationThemesService
from src.products_admin.repository import ProductAdminRepository
from src.products_admin.service import ProductAdminService


async def get_category_service() -> CategoryService:
    repository = CategoryRepository()
    return CategoryService(repository)

def get_facet_type_service() -> FacetTypeService:
    repository = FacetTypeRepository()
    return FacetTypeService(repository)

async def get_facet_service() -> FacetService:
    repository = FacetRepository()
    return FacetService(repository)

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
