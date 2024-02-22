import fastapi
from fastapi import Body, Depends

from src.schemes.py_object_id import PyObjectId
from .schemes import create
from .schemes import get
from .schemes import update
from .schemes.delete import DeleteProductRequest
from .service import ProductAdminService
from src.dependencies.service_dependencies.products_admin import get_product_admin_service

router = fastapi.APIRouter(
    prefix="/admin/products",
    tags=["Products-admin"]
)

@router.get("/create", response_model=create.ProductCreateForm)
async def product_create_form(category_id: PyObjectId,
                              service: ProductAdminService = Depends(get_product_admin_service)):
    """Returns all essential data for product creation"""
    return await service.get_product_creation_essentials(category_id)

@router.post("/create", status_code=fastapi.status.HTTP_201_CREATED, response_model=create.CreateProductResponse)
async def product_create(product: create.CreateProduct = Body(...),
                         service: ProductAdminService = Depends(get_product_admin_service)):
    return await service.create_product(product)

@router.get("/", response_model=get.ProductListResponse)
async def product_list(page: int = fastapi.Query(1, ge=1, ),
                       page_size: int = fastapi.Query(10, ge=1),
                       service: ProductAdminService = Depends(get_product_admin_service)):
    return await service.get_product_list(page, page_size)

@router.get("/search", response_model=get.ProductSearchResponse)
async def product_search_by_name(name: str = "", page: int = fastapi.Query(1, ge=1, ),
                                 page_size: int = fastapi.Query(10, ge=1),
                                 filters: get.ProductSearchFilters = Depends(get.ProductSearchFilters),
                                 service: ProductAdminService = Depends(get_product_admin_service)):
    return await service.search_product(name, filters, page, page_size)

@router.get("/{product_id}", response_model=get.ProductDetailResponse)
async def product_detail(product_id: PyObjectId, service: ProductAdminService = Depends(get_product_admin_service)):
    return await service.get_product_by_id(product_id)

@router.put("/{product_id}", response_model=update.UpdateProductResponse)
async def product_update(product_id: PyObjectId, data_to_update: update.UpdateProduct = Body(...),
                         service: ProductAdminService = Depends(get_product_admin_service)):
    return await service.update_product(product_id, data_to_update)

@router.delete("/{product_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def product_delete(product_id: PyObjectId, service: ProductAdminService = Depends(get_product_admin_service)):
    await service.delete_one_product(product_id)

@router.delete("/", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def product_delete_many(delete_data: DeleteProductRequest = Body(...),
                              service: ProductAdminService = Depends(get_product_admin_service)):
    await service.delete_many_products(delete_data.product_ids)
