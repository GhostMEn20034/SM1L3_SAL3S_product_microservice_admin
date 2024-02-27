from src.apps.search_terms.repository import SearchTermsRepository
from src.apps.search_terms.service import SearchTermsAdminService


async def get_search_terms_service() -> SearchTermsAdminService:
    search_terms_repository = SearchTermsRepository()
    return SearchTermsAdminService(search_terms_repository)