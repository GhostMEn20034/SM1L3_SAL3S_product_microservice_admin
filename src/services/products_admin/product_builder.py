from typing import Tuple, Optional
from bson import ObjectId


class ProductBuilder:
    def __init__(self, product_data: dict):
        self.product_data = product_data

    async def _build_common_product_data(self):
        # get extra attrs from the product data
        # if extra attrs is None, then the value will be an empty list
        extra_attrs = self.product_data["extra_attrs"] if self.product_data.get("extra_attrs") else []
        # Form a dictionary with the common product data
        common_data = {
            "search_terms": self.product_data.get("search_terms", []),
            "for_sale": self.product_data.get("for_sale"),  # is product for sale
            "same_images": self.product_data.get("same_images"),  # Do parent product
            # and product variations have the same images
            "variation_theme": self.product_data.get("variation_theme"),  # variation theme
            "is_filterable": self.product_data.get("is_filterable"),  # Are product's attributes can be used in filters?
            "category": self.product_data.get("category"),  # product category
            "attrs": self.product_data.get("attrs", []),  # main attributes
            "extra_attrs": extra_attrs,  # extra attributes
        }
        return common_data

    async def build_single_product(self, parent: bool = False) -> dict:
        """
        Builds the data for a single product without children or for a parent product
        :param parent: If true, the product will be considering as parent
        """
        # get base attributes from the product data
        base_attrs = self.product_data.get("base_attrs", {})
        common_data = await self._build_common_product_data()
        return {
            **base_attrs,
            "parent": parent,
            "parent_id": None,
            **common_data,
            "is_filterable": False if parent else common_data.get("is_filterable"),
            "for_sale": False if parent else common_data.get("for_sale"),
        }

    async def build_product_variations(self, parent_id: ObjectId, return_images: bool = True) -> Tuple[
        list[dict], Optional[list[dict]]]:
        """
        Builds the data for a product variations.
        :param parent_id: The parent product identifier
        :param return_images: If true, the images will be returned
        """
        # get product variations
        variations = self.product_data.get("variations")
        common_data = await self._build_common_product_data()
        attrs = common_data.get("attrs")

        product_variations = []
        images_to_upload = []
        for variation in variations:
            variation_attrs = variation.get("attrs")
            images = variation.pop("images", None)
            images_to_upload.append(images)  # Append individual images lists
            data_to_insert = {
                **variation, # unpack variation's base attributes
                "parent": False, # Is a parent product
                "parent_id": parent_id, # id of parent (For parent product or product without children value is None)
                **common_data, # unpack products' common data
                "attrs": attrs + variation_attrs, # concatenate parent attributes and variation attributes
            }
            product_variations.append(data_to_insert)

        return product_variations, images_to_upload if return_images else None
