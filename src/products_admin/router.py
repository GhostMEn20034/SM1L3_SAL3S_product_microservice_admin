import fastapi
from src.schemes import PyObjectId
from . import services
from . import schemes

router = fastapi.APIRouter(
    prefix="/admin/products",
    tags=["Products-admin"]
)

@router.get("/create", response_model=schemes.ProductCreateForm)
async def product_create_form(category_id: PyObjectId):
    """Returns all facets and variation themes related with specified category"""
    facets_and_variation_themes = await services.get_facets_and_variation_themes(category_id)
    return facets_and_variation_themes
