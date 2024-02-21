from typing import Union

from src.apps.deals_admin.schemes.base import DealBase, ParentDealBase
from src.apps.deals_admin.schemes.create import CreateDealSchema
from src.apps.deals_admin.schemes.update import UpdatedDeal, UpdateDealSchema, UpdatedParentDeal
from src.schemes.product_filters import ProductFilters
from src.services.product_filter_generator import ProductFilterGenerator


def generate_query_string(data: Union[DealBase, UpdatedDeal]) -> str:
    """Generates the query string from the deal data and other filters."""
    grouped_product_filters = None
    if data.other_filters:
        data = data.dict()
        grouped_product_filters = ProductFilterGenerator.group_chosen_facets_by_code(data["other_filters"])
    else:
        data = data.dict()

    query_string = ProductFilterGenerator(
        ProductFilters.parse_obj({**data, "chosen_facets": grouped_product_filters})
    ).filters_to_query_string()

    return query_string

def prepare_create_deal_data(data: CreateDealSchema, is_parent: bool) -> dict:
    """Prepares the deal data for insertion based on parent/child status."""
    if is_parent:
        return ParentDealBase(**data.dict()).dict()

    deal_data = DealBase(**data.dict())
    deal_data_dict = deal_data.dict()
    query_string = generate_query_string(deal_data)
    return {**deal_data_dict, "query_string": query_string}

def prepare_update_deal_data(data: UpdateDealSchema, is_parent: bool) -> dict:
    """Prepares the deal data for update based on parent/child status."""
    if is_parent:
        return UpdatedParentDeal(**data.dict()).dict()

    deal_data = UpdatedDeal(**data.dict())
    deal_data_dict = deal_data.dict()
    query_string = generate_query_string(deal_data)

    return {**deal_data_dict, "query_string": query_string}
