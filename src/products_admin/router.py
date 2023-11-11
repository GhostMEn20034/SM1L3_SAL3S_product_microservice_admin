import fastapi
from fastapi import Body, BackgroundTasks
from src.schemes import PyObjectId
from .services import create_product_logic
from . import schemes


router = fastapi.APIRouter(
    prefix="/admin/products",
    tags=["Products-admin"]
)

@router.get("/create", response_model=schemes.ProductCreateForm)
async def product_create_form(category_id: PyObjectId):
    """Returns all facets and variation themes related with specified category"""
    facets_and_variation_themes = await create_product_logic.get_facets_and_variation_themes(category_id)
    return facets_and_variation_themes

@router.post("/create", status_code=fastapi.status.HTTP_201_CREATED, response_model=schemes.CreateProductResponse)
async def product_create(background_tasks: BackgroundTasks, product: schemes.CreateProduct = Body(...)):
    return await create_product_logic.create_product(product, background_tasks)
