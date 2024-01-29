from math import ceil
from fastapi.exceptions import HTTPException
from bson import ObjectId

from .repository import FacetRepository
from src.products_admin.service import ProductAdminService


class FacetService:
    """
    Responsible for facet business logic
    """
    def __init__(self, repository: FacetRepository, product_service: ProductAdminService):
        self.repository = repository
        self.product_service = product_service

    async def create_facet(self, data: dict) -> None:
        # try to find facet with the code "data.code"
        facet = await self.repository.get_one_facet({"code": data.get("code")}, {"_id": 1})
        # if there is a facet
        if facet:
            # then raise HTTP 400
            raise HTTPException(
                status_code=400,
                detail={"code": f"Facet with {data.get('code')} code already exists"}
            )
        # return True if there's inserted id, otherwise False
        created_facet = await self.repository.create_facet(data)

        if not created_facet.inserted_id:
            raise HTTPException(status_code=400, detail="Facet not created")

    async def get_facets_for_choices(self) -> list:
        return await self.repository.get_facet_list(projection={"name": 1, "code": 1, "_id": 0})

    async def get_facets(self, filters: dict, page: int, page_size: int) -> dict:
        facets = await self.repository.get_facet_list_with_facets_count(filters, page, page_size)
        # If there are no results
        # then return default result
        if not facets.get("result"):
            result = {
                "result": [],
                "page_count": 1,
            }
            return result

        facets_count = facets.get("total_count").get("total")

        result = {
            "result": facets.get("result"),
            "page_count": ceil(facets_count / page_size), # Calculating count of pages
        }
        # return result
        return result

    async def get_facet_by_id(self, facet_id: ObjectId) -> dict:
        facet = await self.repository.get_one_facet({"_id": facet_id})
        # if there's no facet with the specified id raise HTTP 404 Not Found
        if not facet:
            raise HTTPException(status_code=404, detail="Facet not found")
        # Otherwise return facet with the given id
        return facet

    async def update_facet(self, facet_id: ObjectId, data_to_update: dict) -> None:
        facet = await self.repository.get_one_facet({"_id": facet_id}, {"_id": 1, "code": 1})
        # if there's no facet with the specified id raise HTTP 404 Not Found
        if not facet:
            raise HTTPException(status_code=404, detail="Facet not found")
        # Otherwise update facets
        await self.repository.update_facet({"_id": facet_id}, {"$set": data_to_update})
        await self.product_service.update_attribute_explanation(facet.get("code"),
                                                                data_to_update.get("explanation"))

    async def delete_facet(self, facet_id: ObjectId) -> None:
        facet = await self.repository.get_one_facet({"_id": facet_id}, {"_id": 1})
        # if there's no facet with such id, raise HTTP 404 Not Found
        if not facet:
            raise HTTPException(status_code=404, detail="Facet not found")
        # Otherwise delete facet
        await self.repository.delete_facet({"_id": facet_id})
