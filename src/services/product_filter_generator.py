from urllib.parse import urlencode
import base64
import json
from typing import List, Dict
from src.schemes.product_filters import ProductFilters, AttributeFilterElement, FacetObject


class ProductFilterGenerator:
    def __init__(self, product_filters: ProductFilters):
        self.product_filters = product_filters

    @staticmethod
    def group_chosen_facets_by_code(chosen_facets: List[Dict]) -> Dict[str, FacetObject]:
        """
        :param chosen_facets: List of dictionaries with keys: 'code', 'value', 'unit
        """
        grouped_chosen_facets = {}
        for facet in chosen_facets:
            chosen_facet = AttributeFilterElement(**facet)
            if facet['code'] not in grouped_chosen_facets:
                grouped_chosen_facets[facet['code']] = FacetObject(is_range=False, values=[])

            grouped_chosen_facets[facet['code']].values.append(chosen_facet)

        return grouped_chosen_facets

    @staticmethod
    def convert_chosen_facets_to_base64(chosen_facets: Dict[str, FacetObject]) -> bytes:
        processed_data = {}
        for code, facet_object in chosen_facets.items():
            processed_data[code] = facet_object.dict()

        return base64.urlsafe_b64encode(json.dumps(processed_data).encode())

    def filters_to_query_string(self) -> str:
        query_params = {}

        if self.product_filters.query:
            query_params["q"] = self.product_filters.query

        if self.product_filters.category_id:
            query_params["category"] = self.product_filters.category_id

        if self.product_filters.price_min:
            query_params["minPrice"] = self.product_filters.price_min

        if self.product_filters.price_max:
            query_params["maxPrice"] = self.product_filters.price_max

        if self.product_filters.chosen_facets:
            encoded_facets = self.convert_chosen_facets_to_base64(self.product_filters.chosen_facets)
            query_params["chosenFacets"] = encoded_facets

        return urlencode(query_params)
