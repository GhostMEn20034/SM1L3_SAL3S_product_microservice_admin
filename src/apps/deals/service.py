from datetime import datetime
from math import ceil
from typing import Optional, Union, Dict
from fastapi.exceptions import HTTPException
from bson import ObjectId

from .schemes.base import Deal, ParentDeal
from .schemes.create import CreateDealSchema
from .schemes.update import UpdateDealSchema
from .repository import DealRepository
from src.apps.categories.repository import CategoryRepository
from src.apps.facets.repository import FacetRepository
from src.utils import convert_decimal, is_valid_url
from src.services.deals.upload_deal_images import upload_deal_image
from src.services.deals.deal_validator import DealValidatorCreate, DealValidatorUpdate
from src.services.deals.prepare_deal_data import prepare_create_deal_data, prepare_update_deal_data
from src.services.deals.delete_deal_images import delete_deal_image


class DealAdminService:
    """
    Responsible for deal business logic
    """

    def __init__(self, deal_repository: DealRepository, category_repository: CategoryRepository,
                 facet_repository: FacetRepository):
        self.deal_repository = deal_repository
        self.category_repository = category_repository
        self.facet_repository = facet_repository

    async def get_deal_creation_essentials(self, facet_category: Optional[ObjectId] = None):
        facet_filters = {"is_range": False}
        if facet_category:
            # filter to get facets that belong to all categories or to category in "facet_category" variable
            facet_filters["categories"] = {"$in": [facet_category, "*"]}

        facets = await self.facet_repository.get_facet_list(facet_filters,
                                                            {"explanation": 0, "show_in_filters": 0, "categories": 0})
        categories = await self.category_repository.get_category_list({"level": {"$gt": 0}},
                                                                      {"name": 1})
        parent_deals = await self.deal_repository.get_deal_list({"is_parent": True}, {"name": 1})

        return {
            "categories": categories,
            "parent_deals": parent_deals,
            "facets": facets,
        }

    async def get_deals(self, page: int, page_size: int) -> dict:
        deals = await self.deal_repository.get_deal_list_with_deals_count(page, page_size)
        # If there are no results
        # then return default response
        if not deals.get("result"):
            result = {
                "result": [],
                "page_count": 1,
            }
            return result

        deals_count = deals.get("total_count").get("total")

        result = {
            "result": deals.get("result"),
            "page_count": ceil(deals_count / page_size),
        }
        # return result
        return result

    async def get_deal_by_id(self, deal_id: ObjectId) -> Dict[str, Union[Deal, ParentDeal]]:
        deal = await self.deal_repository.get_one_deal({"_id": deal_id})
        # if there's no deal with the specified id raise HTTP 404 Not Found
        if not deal:
            raise HTTPException(status_code=404, detail="deal not found")
        # Otherwise return deal with the given id

        if deal["is_parent"]:
            return {"deal": ParentDeal(**deal)}

        return {"deal": Deal(**deal)}

    async def create_deal(self, data: CreateDealSchema) -> None:
        deal_validator = DealValidatorCreate(data)
        errors = await deal_validator.validate()
        if errors:
            raise HTTPException(status_code=400, detail=errors)

        image = data.image
        is_parent = data.is_parent
        data_to_insert = prepare_create_deal_data(data, is_parent)

        current_date = datetime.utcnow()
        data_to_insert.update({
            "created_at": current_date,
            "modified_at": current_date
        })
        convert_decimal(data_to_insert)
        inserted_deal = await self.deal_repository.create_deal(data_to_insert)
        uploaded_image_url = await upload_deal_image(image, f"{inserted_deal.inserted_id}_0.jpg")
        await self.deal_repository.update_deal({"_id": inserted_deal.inserted_id},
                                               {"$set": {"image": uploaded_image_url}})

    async def update_deal(self, deal_id: ObjectId, data_to_update: UpdateDealSchema) -> None:
        deal = await self.deal_repository.get_one_deal({"_id": deal_id}, {"is_parent": 1})
        # if there's no deal with the specified id raise HTTP 404 Not Found
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        deal_validator = DealValidatorUpdate(data_to_update)
        errors = await deal_validator.validate()
        if errors:
            raise HTTPException(status_code=400, detail=errors)

        # if there's an image value and it is not valid url
        if not is_valid_url(data_to_update.image) and data_to_update.image is not None:
            await upload_deal_image(data_to_update.image, f"{deal_id}_0.jpg")

        data_to_update = prepare_update_deal_data(data_to_update, deal["is_parent"])
        data_to_update.pop("image")

        current_date = datetime.utcnow()
        data_to_update["modified_at"] = current_date

        convert_decimal(data_to_update)
        await self.deal_repository.update_deal({"_id": deal_id}, {"$set": data_to_update})

    async def delete_deal(self, deal_id: ObjectId) -> None:
        deal = await self.deal_repository.get_one_deal({"_id": deal_id},
                                                       {"_id": 1, "is_parent": 1, "image": 1})
        # if there's no deal with such id, raise HTTP 404 Not Found
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        if deal["is_parent"]:
            child_deals = await self.deal_repository.get_deal_list({"parent_id": deal_id},
                                                                   {"_id": 1})
            if child_deals:
                raise HTTPException(status_code=400, detail="You cannot delete parent deal if it has child deals")

        await delete_deal_image(deal["image"])
        await self.deal_repository.delete_deal({"_id": deal_id})
