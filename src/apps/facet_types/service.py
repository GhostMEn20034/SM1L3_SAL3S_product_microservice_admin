from .repository import FacetTypeRepository

class FacetTypeService:
    def __init__(self, repository: FacetTypeRepository):
        self.repository = repository

    async def get_facet_types(self):
        return await self.repository.get_facet_type_list()