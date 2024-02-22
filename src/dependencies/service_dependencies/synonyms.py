from src.apps.synonyms.repository import SynonymRepository
from src.apps.synonyms.service import SynonymService


async def get_synonym_service() -> SynonymService:
    repository = SynonymRepository()
    return SynonymService(repository)
