from src.apps.categories_admin.repository import CategoryRepository
from src.apps.facet_types.repository import FacetTypeRepository
from src.apps.facets.repository import FacetRepository
from src.apps.products_admin.repository import ProductAdminRepository
from src.apps.products_admin.service import ProductAdminService
from src.apps.variaton_themes.repository import VariationThemeRepository


async def get_product_admin_service() -> ProductAdminService:
    product_repo = ProductAdminRepository()
    category_repo = CategoryRepository()
    facet_repo = FacetRepository()
    variation_theme_repo = VariationThemeRepository()
    facet_type_repo = FacetTypeRepository()
    return ProductAdminService(product_repo, category_repo, facet_repo, variation_theme_repo, facet_type_repo)