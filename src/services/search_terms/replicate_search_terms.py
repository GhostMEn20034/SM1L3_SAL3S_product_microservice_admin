from typing import List
from src.apps.search_terms.service import SearchTermsAdminService
from src.dependencies.service_dependencies.search_terms import get_search_terms_service

async def replicate_search_terms(search_terms: List[str], session=None):
    """
    Replicates search terms to search_terms collection
    """
    search_terms_service: SearchTermsAdminService = await get_search_terms_service()
    await search_terms_service.create_search_terms_if_not_exist(search_terms, session)
