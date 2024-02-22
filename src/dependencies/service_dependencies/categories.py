from src.apps.categories_admin.repository import CategoryRepository
from src.apps.categories_admin.service import CategoryService


async def get_category_service() -> CategoryService:
    repository = CategoryRepository()
    return CategoryService(repository)