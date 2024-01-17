from math import ceil
from typing import Tuple, Optional, List, Dict, Union, Any
from bson import ObjectId
from fastapi import HTTPException

from src.categories_admin.repository import CategoryRepository
from src.database import client
from src.facet_types.repository import FacetTypeRepository
from src.facets.repository import FacetRepository
from src.settings import BUCKET_BASE_URL
from src.utils import convert_decimal
from src.variaton_themes.repository import VariationThemeRepository
from src.services.products_admin.product_builder import ProductBuilder
from .repository import ProductAdminRepository
from .schemes.create import CreateProduct
from .schemes.update import UpdateProduct
from .utils import remove_product_attrs, set_attr_non_optional
from src.services.products_admin.validators import ProductValidatorCreate, ProductValidatorUpdate
from src.services.products_admin.product_image_upload_manager import ProductImageUploadManager


class ProductAdminService:
    def __init__(self, product_repo: ProductAdminRepository, category_repo: CategoryRepository,
                 facet_repo: FacetRepository, variation_theme_repo: VariationThemeRepository,
                 facet_type_repo: FacetTypeRepository):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.facet_repo = facet_repo
        self.variation_theme_repo = variation_theme_repo
        self.facet_type_repo = facet_type_repo

    @staticmethod
    async def _get_var_theme_field_codes(variation_theme: dict):
        """
        Return Variation theme field codes
        :param variation_theme: Dict that stored in product object
        """
        # Get variation theme options
        var_theme_options = variation_theme.get("options", [])
        # stores all variation theme field codes
        field_codes = []
        # get all variation theme field codes
        for option in var_theme_options:
            field_codes.extend(option.get("field_codes", []))

        return field_codes

    async def get_product_creation_essentials(self, category_id: ObjectId):
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

    async def _insert_products_to_db(self, product_data: dict) -> Tuple[ObjectId, Optional[List[ObjectId]]]:
        """
        Inserts products to database
        :param product_data: Product data to be inserted
        """
        product_data["for_sale"] = True
        has_variations = product_data.get("has_variations", False)
        same_images = product_data.get("same_images", True)
        product_builder = ProductBuilder(product_data)
        image_upload_manager = ProductImageUploadManager(same_images,
                                                         product_data.get("images"),
                                                         product_repo=self.product_repo)

        # Set "optional" property in each product's attribute
        product_data["attrs"] = await set_attr_non_optional(product_data["attrs"])

        if has_variations:
            async with (await client.start_session() as session):
                async with session.start_transaction():
                    # Set "optional" property in each variations' attribute
                    for variation in product_data.get("variations"):
                        variation["attrs"] = await set_attr_non_optional(variation["attrs"])
                    # Build data for parent product
                    parent_data = await product_builder.build_single_product(parent=True)
                    # Create parent product
                    inserted_parent = await self.product_repo.create_one_product(parent_data, session=session)
                    parent_id = inserted_parent.inserted_id
                    # get variation theme field codes
                    field_codes = await self._get_var_theme_field_codes(product_data.get("variation_theme", {}))
                    # remove parent's attributes
                    product_data["attrs"] = await remove_product_attrs(product_data["attrs"], field_codes)
                    # build data for product variations
                    variation_data, variation_imgs = await product_builder \
                        .build_product_variations(parent_id, return_images=not same_images)
                    # Insert product variations
                    inserted_variations = await self.product_repo.create_many_products(variation_data, session=session)
                    variation_ids = inserted_variations.inserted_ids
                    # Upload images in another process
                    await image_upload_manager.upload_images_multiple_products(parent_id,
                                                                               variation_ids,
                                                                               variation_imgs,
                                                                               update_parent_images=True,
                                                                               another_process=True)
                    # return parent id and list of inserted products' ids
                    return parent_id, variation_ids

        single_product_data = await product_builder.build_single_product()
        # Create single product
        inserted_single_product = await self.product_repo.create_one_product(single_product_data)
        single_product_id = inserted_single_product.inserted_id
        # Upload images in another process
        await image_upload_manager.upload_images_one_product(single_product_id, another_process=True)
        # return parent id and list of inserted products' ids
        return single_product_id, None

    async def create_product(self, data: CreateProduct) -> Dict[str, Union[ObjectId, List[ObjectId]]]:
        """
        Creates product with the specified data if there are no errors.
        :param data: CreateProduct model containing product data.
        """
        category = await self.category_repo.get_one_category({"_id": data.category}, {"_id": 1})
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category specified")

        product_validator = ProductValidatorCreate(product=data)
        # Validate product data
        validated_data, errors = await product_validator.validate()
        if errors:
            raise HTTPException(status_code=400, detail=errors)

        # convert all decimal fields into decimal128
        validated_data = convert_decimal(validated_data)
        product_id, variation_ids = await self._insert_products_to_db(product_data=validated_data)
        return {"product_id": product_id, "variation_ids": variation_ids}

    async def update_product(self, product_id: ObjectId, data: UpdateProduct):
        # Try to find a product
        product: dict = await self.product_repo \
            .get_one_product({"_id": product_id},
                             {"variation_theme": 1, "parent": 1, "same_images": 1, "images": 1})
        # if it was not found, then return HTTP 404 Not Found to the client
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Initialize validator of product data to update
        product_validator = ProductValidatorUpdate(product=data, extra_data={"same_images": product["same_images"],
                                                                             "parent": product["parent"]})
        # Get validated product data and get errors
        validated_data, errors = await product_validator.validate()
        # If there are errors, then raise HTTP 400 to the client
        if errors:
            raise HTTPException(status_code=400, detail=errors)

        return {"Sound": "UWU"}

    async def get_product_list(self, page: int, page_size: int) -> dict:
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
                # list of products
                "products": [],
                # Count of pages
                "page_count": 1,
                # Count of products
                "items_count": 0,
            }
        # otherwise, return product list, product count, page count from query
        products_count = product_list.get("count", 0)

        result = {
            # list of products
            "products": product_list.get("items", []),
            # Count of pages
            "page_count": ceil(products_count / page_size),
            # Count of products
            "items_count": products_count,
        }
        return result

    async def get_product_by_id(self, product_id: ObjectId) -> dict[str, Any]:
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
        # If product is a parent
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
