from math import ceil
from fastapi.exceptions import HTTPException
from .repository import VariationThemeRepository
from src.schemes.py_object_id import PyObjectId

class VariationThemesService:
    """
        Responsible for variation theme business logic
    """
    def __init__(self, repository: VariationThemeRepository):
        self.repository = repository

    async def get_variation_themes(self, page: int, page_size: int):
        variation_themes = await self.repository.get_variation_themes_with_doc_count(page, page_size)
        # If there are no results
        # then return default result
        if not variation_themes.get("result"):
            result = {
                "result": [],
                "page_count": 1,
            }
            return result

        # get variation theme count
        var_theme_count = variation_themes.get("total_count").get("total")

        result = {
            "result": variation_themes.get("result"),
            "page_count": ceil(var_theme_count / page_size), # Calculating count of pages
        }

        return result

    async def get_variation_theme_by_id(self, variation_theme_id: PyObjectId):
        variation_theme = await self.repository.get_one_variation_theme({"_id": variation_theme_id})
        if not variation_theme:
            raise HTTPException(status_code=404, detail="Variation theme not found")

        return variation_theme

    async def update_variation_theme(self, variation_theme_id: PyObjectId, data: dict):
        variation_theme = await self.repository.get_one_variation_theme({"_id": variation_theme_id})
        if not variation_theme:
            raise HTTPException(status_code=404, detail="Variation theme not found")

        await self.repository.update_variation_theme({"_id": variation_theme_id}, {"$set": data})

    async def create_variation_theme(self, data: dict):
        created_variation_theme = await self.repository.create_variation_theme(data)
        if not created_variation_theme.inserted_id:
            raise HTTPException(status_code=400, detail="Variation theme not created")

    async def delete_variation_theme(self, variation_theme_id: PyObjectId):
        variation_theme = await self.repository.get_one_variation_theme({"_id": variation_theme_id})
        if not variation_theme:
            raise HTTPException(status_code=404, detail="Variation theme not found")

        await self.repository.delete_variation_theme({"_id": variation_theme_id})
