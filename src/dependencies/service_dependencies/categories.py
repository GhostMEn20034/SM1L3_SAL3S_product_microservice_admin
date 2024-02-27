from src.apps.categories.repository import CategoryRepository
from src.apps.categories.service import CategoryService


async def get_category_service() -> CategoryService:
    repository = CategoryRepository()
    return CategoryService(repository)