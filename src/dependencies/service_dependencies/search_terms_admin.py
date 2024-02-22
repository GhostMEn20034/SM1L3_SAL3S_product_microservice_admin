from src.apps.search_terms_admin.repository import SearchTermsRepository
from src.apps.search_terms_admin.service import SearchTermsAdminService


async def get_search_terms_admin_service() -> SearchTermsAdminService:
    search_terms_repository = SearchTermsRepository()
    return SearchTermsAdminService(search_terms_repository)