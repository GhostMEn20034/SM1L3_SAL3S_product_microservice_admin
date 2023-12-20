from src.database import db
from src.utils import convert_decimal

from src.products_admin.services.product_validation import (
    validate_product_images,
    validate_product_variations
)
from src.schemes import PyObjectId

from src.products_admin.schemes.create import CreateProduct
from src.products_admin.utils import AttrsHandler
from src.products_admin.services.insert_products import insert_product_to_db

from fastapi.exceptions import HTTPException


async def get_facets_and_variation_themes(category_id: PyObjectId):
    category = await db.categories.find_one({"_id": category_id}, {"tree_id": 0, "parent_id": 0})

    if not category:
        raise HTTPException(status_code=404, detail="Category with the specified id doesn't exist")

    facets = await db.facets.find(
        {
            "$or": [
                {"categories": category_id},
                {"categories": "*"}
            ],
            "code": {"$ne": "price"}
        },
        {
            "categories": 0
        }
    ).to_list(length=None)

    variation_themes = await db.variation_themes.find(
        {
            "$or": [
                {"categories": category_id},
                {"categories": "*"}
            ]
        },
        {
            "categories": 0
        }
    ).to_list(length=None)

    facet_types = await db.facet_types.find({"value": {"$ne": "list"}}).to_list(length=None)

    return {
        "facets": facets,
        "variation_themes": variation_themes,
        "facet_types": facet_types,
        "category": category,
    }


async def create_product(data: CreateProduct):
    # Dict with product data errors
    errors = {}

    # product data converted from pydantic class to normal python datatypes
    product_data = data.dict()
    # if there's no category, then raise HTTP 400 Bad Request
    if not await db.categories.count_documents({"_id": product_data["category"]}, limit=1):
        raise HTTPException(status_code=400, detail="Incorrect category specified")

    # product attributes
    attrs = product_data.get("attrs")
    # Attributes handler instance
    attr_handler = AttrsHandler(attrs)
    # Validate attributes
    validated_attrs, attrs_errors = attr_handler.validate_attrs_values()
    product_data["attrs"] = validated_attrs
    # if there are errors after attributes validation
    if attrs_errors:
        # add attr errors to the dict with errors
        errors["attrs"] = attrs_errors

    # Additional product attributes
    extra_attrs = product_data.get("extra_attrs", [])
    # If there are extra attributes
    if extra_attrs:
        extra_attr_handler = AttrsHandler(extra_attrs)
        # Validate extra attributes
        extra_attrs, extra_attrs_errors = extra_attr_handler.validate_attrs_values(
            del_optional_invalid_attrs=False
        )
        product_data["extra_attrs"] = extra_attrs
        # if there are errors after extra attributes validation
        if extra_attrs_errors:
            # add extra attr errors to the dict with errors
            errors["extra_attrs"] = extra_attrs_errors

    # If there are images in product_data
    if images := product_data.get("images"):
        # Then, validate images in product_data
        await validate_product_images(images, errors)

    # if field has_variations is True and there are product variations
    if (has_variations := product_data.get("has_variations")) \
        and (variations := product_data.get("variations")):
        # Check product variations for errors
        variation_errors = await validate_product_variations(variations,
                                                             has_variations and not product_data.get("same_images"))
        # if there are errors in product variations
        if variation_errors:
            # Then, add variation errors to the dict with errors
            errors["variations"] = variation_errors

    # if there are errors
    if errors:
        # Then raise HTTP 400 Bad Request and pass errors in detail parameter
        raise HTTPException(status_code=400, detail=errors)

    # convert all decimal fields into decimal128
    product_data = convert_decimal(product_data)
    product, product_variations = await insert_product_to_db(product_data)

    return {"product_id": product, "variation_ids": product_variations}
