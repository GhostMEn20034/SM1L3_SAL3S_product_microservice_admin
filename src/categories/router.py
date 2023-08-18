import fastapi
from typing import List, Annotated
from .services import get_categories
from .schemes import Category

router = fastapi.APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/", response_model=List[Category])
async def category_list():
    categories = await get_categories()
    return categories
