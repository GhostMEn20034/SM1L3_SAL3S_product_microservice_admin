from src.apps.facet_types.repository import FacetTypeRepository
from src.apps.facet_types.service import FacetTypeService


def get_facet_type_service() -> FacetTypeService:
    repository = FacetTypeRepository()
    return FacetTypeService(repository)