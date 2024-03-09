from src.utils import async_worker
from src.worker import celery
from src.dependencies.service_dependencies.search_terms import get_search_terms_service
from src.apps.search_terms.service import SearchTermsAdminService
from src.celery_logger import logger

@celery.task(name='reset_search_count')
def reset_search_count():
    logger.info(f"Ran periodic task reset_search_count")
    search_terms_service: SearchTermsAdminService = async_worker(get_search_terms_service, )
    async_worker(search_terms_service.reset_search_count, )