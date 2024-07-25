import fastapi
from fastapi import Depends

from .services import VariationThemesService
from . import schemes
from src.schemes.py_object_id import PyObjectId
from src.dependencies.service_dependencies.variation_themes import get_variation_theme_service

router = fastapi.APIRouter(
    prefix='/admin/variation-themes',
    tags=['Variation themes'],
)


@router.get("/", response_model=schemes.VariationThemeResult)
async def variation_themes_list(page: int = fastapi.Query(1, ge=1),
                                page_size: int = fastapi.Query(15, ge=0),
                                service: VariationThemesService = Depends(get_variation_theme_service)
                                ):
    result = await service.get_variation_themes(page, page_size)
    return result

@router.get("/{variation_theme_id}", response_model=schemes.VariationTheme)
async def variation_theme_detail(variation_theme_id: PyObjectId,
                                 service: VariationThemesService = Depends(get_variation_theme_service)):
    result = await service.get_variation_theme_by_id(variation_theme_id)
    return result


@router.put("/{variation_theme_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def variation_theme_update(variation_theme_id: PyObjectId, data: schemes.VariationThemeUpdate,
                                 service: VariationThemesService = Depends(get_variation_theme_service)):
    await service.update_variation_theme(variation_theme_id, data.dict())


@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def variation_theme_create(data: schemes.VariationThemeCreate,
                                 service: VariationThemesService = Depends(get_variation_theme_service)):
    await service.create_variation_theme(data.dict())


@router.delete("/{variation_theme_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def variation_theme_delete(variation_theme_id: PyObjectId,
                                 service: VariationThemesService = Depends(get_variation_theme_service)):
    await service.delete_variation_theme(variation_theme_id)
