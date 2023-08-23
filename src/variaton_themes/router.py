import fastapi
import math
from . import services
from . import schemes
from src.schemes import PyObjectId

router = fastapi.APIRouter(
    prefix='/variation-themes',
    tags=['Variation themes']
)


@router.get("/", response_model=schemes.VariationThemeResult)
async def variation_themes_list(page: int = fastapi.Query(1, ge=1),
                     page_size: int = fastapi.Query(15, ge=0)):
    variation_themes = await services.get_variation_themes(page, page_size)

    page_count = variation_themes[0].get("total_count")[0].get("total")

    result = {
        "result": variation_themes[0].get("result"),
        "page_count": math.ceil(page_count / page_size)
    }

    return result


@router.get("/{variation_theme_id}", response_model=schemes.VariationTheme)
async def variation_theme_detail(variation_theme_id: PyObjectId):
    variation_theme = await services.get_variation_theme_by_id(variation_theme_id)

    if not variation_theme:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="Variation theme not found")

    return variation_theme
