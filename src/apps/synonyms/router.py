import fastapi

from .schemes.get import SynonymListResponse, SynonymDetailResponse
from .schemes.create import SynonymCreate
from .schemes.update import SynonymUpdate
from .service import SynonymService
from src.dependencies.service_dependencies import get_synonym_service
from src.schemes.py_object_id import PyObjectId

router = fastapi.APIRouter(
    prefix='/admin/synonyms',
    tags=["Synonyms"]
)


@router.get("/create")
async def get_synonym_creation_essentials(service: SynonymService = fastapi.Depends(get_synonym_service)):
    return await service.get_synonym_creation_essentials()


@router.post("/create", status_code=fastapi.status.HTTP_201_CREATED)
async def create_synonym(data: SynonymCreate,
                         service: SynonymService = fastapi.Depends(get_synonym_service)):
    await service.create_synonym(data)


@router.get("/", response_model=SynonymListResponse)
async def get_synonym_list(page: int = fastapi.Query(1, ge=1, ),
                           page_size: int = fastapi.Query(15, ge=0),
                           service: SynonymService = fastapi.Depends(get_synonym_service)):
    return await service.get_synonym_list(page, page_size)


@router.get("/{synonym_id}", response_model=SynonymDetailResponse)
async def get_synonym_details(synonym_id: PyObjectId, service: SynonymService = fastapi.Depends(get_synonym_service)):
    synonym = await service.get_synonym_by_id(synonym_id)
    # get data for forms to update synonyms
    synonym_creation_essentials = await service.get_synonym_creation_essentials()
    return {"synonym": synonym, "creation_essentials": synonym_creation_essentials}


@router.put("/{synonym_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def update_synonym(synonym_id: PyObjectId, data_to_update: SynonymUpdate,
                         service: SynonymService = fastapi.Depends(get_synonym_service)):
    await service.update_synonym(synonym_id, data_to_update)


@router.delete("/{synonym_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_one_synonym(synonym_id: PyObjectId, service: SynonymService = fastapi.Depends(get_synonym_service)):
    await service.delete_one_synonym(synonym_id)
