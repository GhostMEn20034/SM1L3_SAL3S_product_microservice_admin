from decimal import Decimal
from math import ceil
from typing import List, Dict, Union, Any, Optional
from pymongo.operations import UpdateOne
from bson import ObjectId, Decimal128
from fastapi import HTTPException

from src.apps.categories.repository import CategoryRepository
from src.apps.facet_types.repository import FacetTypeRepository
from src.apps.facets.repository import FacetRepository
from src.utils import convert_decimal
from src.apps.variaton_themes.repository import VariationThemeRepository
from .repository import ProductAdminRepository
from .schemes.create import CreateProduct
from .schemes.get import ProductSearchFilters
from .schemes.update import UpdateProduct
from src.services.products.validators import ProductValidatorCreate, ProductValidatorUpdate
from src.services.products.product_crud.product_creator import ProductCreator
from src.services.products.product_crud.product_modifier import ProductModifier
from src.services.products.product_crud.product_remover import ProductRemover
from src.services.products.filters.filter_creator import ProductsFilterCreatorAdmin
from src.services.products.replication.replicate_products import replicate_updated_discounts


class ProductAdminService:
    def __init__(self, product_repo: ProductAdminRepository, category_repo: CategoryRepository,
                 facet_repo: FacetRepository, variation_theme_repo: VariationThemeRepository,
                 facet_type_repo: FacetTypeRepository):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.facet_repo = facet_repo
        self.variation_theme_repo = variation_theme_repo
        self.facet_type_repo = facet_type_repo

    async def get_product_creation_essentials(self, category_id: ObjectId) -> Dict:
        """
        Returns essential data for product creation
        """
        category = await self.category_repo.get_one_category({"_id": category_id},
                                                             {"tree_id": 0, "parent_id": 0})
        if not category:
            raise HTTPException(status_code=404, detail="Category with the specified id doesn't exist")
        # Get all facets that belong to the specified category or all categories
        facets = await self.facet_repo.get_facet_list(
            {"$or": [
                {"categories": category_id},
                {"categories": "*"}
            ],
            },
            {
                "categories": 0
            }
        )
        # Get all variation_themes that belong to the specified category or all categories
        variation_themes = await self.variation_theme_repo.get_variation_theme_list(
            {
                "$or": [
                    {"categories": category_id},
                    {"categories": "*"}
                ]
            },
            {
                "categories": 0
            }
        )
        # get all facet types except the list
        facet_types = await self.facet_type_repo.get_facet_type_list({"value": {"$ne": "list"}})

        return {
            "facets": facets,
            "variation_themes": variation_themes,
            "facet_types": facet_types,
            "category": category,
        }

    async def create_product(self, data: CreateProduct) -> Dict[str, Union[ObjectId, List[ObjectId]]]:
        """
        Creates product with the specified data if there are no errors.
        :param data: CreateProduct model containing product data.
        """
        category = await self.category_repo.get_one_category({"_id": data.category}, {"_id": 1})
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category specified")

        product_validator = ProductValidatorCreate(data, self.product_repo)
        # Validate product data
        validated_data, errors = await product_validator.validate()
        if errors:
            raise HTTPException(status_code=400, detail=errors)

        # convert all decimal fields into decimal128
        validated_data = convert_decimal(validated_data)
        product_creator = ProductCreator(self.product_repo)
        product_id, variation_ids = await product_creator.create_product(validated_data)
        return {"product_id": product_id, "variation_ids": variation_ids}

    async def update_product(self, product_id: ObjectId,
                             data: UpdateProduct) -> Dict[str, Union[ObjectId, List[ObjectId]]]:
        # Try to find a product
        product: dict = await self.product_repo \
            .get_one_product({"_id": product_id},
                             {"variation_theme": 1, "parent": 1, "same_images": 1, "images": 1})
        # if it was not found, then return HTTP 404 Not Found to the client
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Initialize validator of product data to update
        product_validator = ProductValidatorUpdate(product=data,
                                                   extra_data={"same_images": product["same_images"],
                                                               "parent": product["parent"]},
                                                   product_repo=self.product_repo)
        # Get validated product data and get errors
        validated_data, errors = await product_validator.validate()
        # If there are errors, then raise HTTP 400 to the client
        if errors:
            raise HTTPException(status_code=400, detail=errors)
        # Whether product is parent.
        parent = product.get("parent", False)
        # convert all decimal fields into decimal128
        validated_data = convert_decimal(validated_data)

        product_modifier = ProductModifier(self.product_repo)
        result = await product_modifier.update_product(product_id, validated_data, parent)
        return result

    async def get_product_list(self, page: int, page_size: int) -> Dict:
        """
        :param page: Page number.
        :param page_size: Number of products per page.
        :return: A list of products, their variations and total product count on specified page.
        """
        product_list = await self.product_repo.get_products_with_variations(page, page_size)
        if not product_list:
            # If there are no products, then
            # return empty list, page count 0, items count 0
            return {
                "products": [],
                "page_count": 1,
                "items_count": 0,
            }
        # otherwise, return product list, product count, page count from query
        products_count = product_list.get("count")

        result = {
            "products": product_list.get("items", []),
            "page_count": ceil(products_count / page_size),
            "items_count": products_count,
        }
        return result

    async def get_product_by_id(self, product_id: ObjectId) -> Dict[str, Any]:
        """
        Returns product with the specified id if it exists and product variations if they are exist.
        Also, it returns facets, category, facet_types.
        If there's no product with the specified id, it raises HTTPException with status code 404
        """
        product = await self.product_repo.get_product_details(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # get facets where code equals to one from product["attr_codes"] list
        # OR category is equal to product.category or equal to "*"
        facets = await self.facet_repo.get_facet_list(
            {"$or": [
                {"code": {"$in": product.pop("attr_codes", [])}},
                {"categories": {"$in": [product.get("category"), "*"]}}
            ]
            },
        )
        # get category where _id equals to product's category field.
        category = await self.category_repo.get_one_category({"_id": product.get("category")},
                                                             {"_id": 0, "name": 1, "groups": 1})
        # get facet types
        facet_types = await self.facet_type_repo.get_facet_type_list({"value": {"$ne": "list"}},
                                                                     {"_id": 0, })
        if product.get("parent"):
            # get variation theme
            variation_theme = dict(product.get("variation_theme"))
            # initialize list where field_codes from variation theme is stored
            field_codes = []
            for option in variation_theme.pop("options", []):
                # get field_codes from each option in variation theme options
                field_codes.extend(option.get("field_codes", []))
            # Assign field_codes property to list of all field codes in options
            variation_theme["field_codes"] = field_codes
        else:
            variation_theme = None

        result = {
            "product": product,
            "facets": facets,
            "variation_theme": variation_theme,
            "category": category,
            "facet_types": facet_types,
        }
        return result

    async def search_product(self, name: str, filters: ProductSearchFilters, page: int, page_size: int) -> dict:
        filters = await ProductsFilterCreatorAdmin.generate_search_product_filters(filters)
        product_list = await self.product_repo.search_products_by_name(
            name, {**filters, "parent": False},
            projection={"name": 1, "price": 1, "discount_rate": 1, "sku": 1},
            page=page, page_size=page_size
        )
        if not product_list:
            # If there are no products, then
            # return empty list, page count 0, items count 0
            return {"products": [], "page_count": 1, "items_count": 0}
        # otherwise, return product list, product count, page count from query
        products_count = product_list.get("count")
        result = {
            "products": product_list.get("items", []),
            "page_count": ceil(products_count / page_size),
            "items_count": products_count,
        }
        return result

    async def delete_one_product(self, product_id: ObjectId) -> int:
        product = await self.product_repo.get_one_product(
            {"_id": product_id},
            {"parent": 1, "same_images": 1, "images": 1}
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product_remover = ProductRemover(self.product_repo)
        deleted_count = await product_remover.delete_one_product(product)

        return deleted_count

    async def delete_many_products(self, product_ids: List[ObjectId]):
        products = await self.product_repo.get_product_list(
            {"_id": {"$in": product_ids}},
         {"parent": 1, "same_images": 1, "images": 1})

        if not products:
            raise HTTPException(status_code=404, detail="Products with the specified ids are not found")

        product_remover = ProductRemover(self.product_repo)
        deleted_count = await product_remover.delete_many_products(products)
        return deleted_count

    async def update_attribute_explanation(self, code: str, explanation: str) -> int:
        updated_products = await self.product_repo.update_many_products(
            {"attrs": {"$elemMatch": {"code": code}}},
            {"$set": {"attrs.$[elem].explanation": explanation}},
            array_filters=[{"elem.code": code}])
        return updated_products.modified_count

    async def set_product_discounts(self, product_ids: List[ObjectId],
                                       discounts: Optional[List[Union[Decimal, Decimal128]]] = None):
        """
        Sets product discounts for the specified products
        :param product_ids: List of product ids where the method need to update discounts
        :param discounts: List of product discounts which the method need to apply to the products.
        If not provided, all products listed will not have any discount.
        :return: Count of updated products
        """
        if discounts is None:
            updated_products = await self.product_repo.update_many_products({"_id": {"$in": product_ids}},
                                                         {"$set": {"discount_rate": None}})
            await replicate_updated_discounts(product_ids, None)
            return updated_products.modified_count

        if len(product_ids) != len(discounts):
            return 0

        converted_discounts = convert_decimal({"discounts": discounts})

        update_operations = []
        for product_id, discount in zip(product_ids, converted_discounts["discounts"]):
            update_operations.append(UpdateOne({"_id": product_id},
                                               {"$set": {"discount_rate": discount}}))

        updated_products = await self.product_repo.update_many_products_bulk(update_operations)
        await replicate_updated_discounts(product_ids, discounts)
        return updated_products.modified_count
