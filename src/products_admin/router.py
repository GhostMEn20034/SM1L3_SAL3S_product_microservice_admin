import fastapi
from fastapi import Body, BackgroundTasks
from src.schemes import PyObjectId
from .services import create_product_logic, get_products
from .schemes import create
from .schemes import get


router = fastapi.APIRouter(
    prefix="/admin/products",
    tags=["Products-admin"]
)

@router.get("/create", response_model=create.ProductCreateForm)
async def product_create_form(category_id: PyObjectId):
    """Returns all facets and variation themes related with specified category"""
    facets_and_variation_themes = await create_product_logic.get_facets_and_variation_themes(category_id)
    return facets_and_variation_themes

@router.post("/create", status_code=fastapi.status.HTTP_201_CREATED, response_model=create.CreateProductResponse)
async def product_create(background_tasks: BackgroundTasks, product: create.CreateProduct = Body(...)):
    return await create_product_logic.create_product(product, background_tasks)

@router.get("/", response_model=get.ProductListResponse)
async def products_list(page: int = fastapi.Query(1, ge=1,), page_size: int = fastapi.Query(15, ge=0)):
    return await get_products.get_product_list(page, page_size)

@router.get("/{product_id}", response_model=get.ProductDetailResponse)
async def product_detail(product_id: PyObjectId):
    return await get_products.get_product_details(product_id)
