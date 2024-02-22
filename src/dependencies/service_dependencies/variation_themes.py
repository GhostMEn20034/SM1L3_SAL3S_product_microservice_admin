from src.apps.variaton_themes.repository import VariationThemeRepository
from src.apps.variaton_themes.services import VariationThemesService


async def get_variation_theme_service() -> VariationThemesService:
    repository = VariationThemeRepository()
    return VariationThemesService(repository)