from typing import List
from fastapi import HTTPException
from src.database import db
from src.products_admin.utils import AttrsHandler
from src.schemes import PyObjectId
from src.products_admin.schemes.update import UpdateProduct
from .product_validation import validate_image_ops, validate_product_variations


async def update_product(product_id: PyObjectId, data: UpdateProduct):
    # Dict with product data errors
    errors = {}

    # Trying to find a product
    product: dict = await db.products.find_one({"_id": product_id},
                                         {"variation_theme": 1, "parent": 1, "same_images": 1, "images": 1})
    # if it was not found, then return HTTP 404 Not Found to the client
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # convert product data to the dict
    data = data.dict(exclude_none=True, by_alias=True)
    # get product attributes
    attrs: List[dict] = data.get("attrs")
    # Attributes handler instance
    attr_handler = AttrsHandler(attrs)
    # Validate attributes
    validated_attrs, attr_errors = attr_handler.validate_attrs_values()
    data["attrs"] = validated_attrs
    # if there are errors after attributes validation
    if attr_errors:
        # add attr errors to the dict with errors
        errors["attrs"] = attr_errors

    # Additional product attributes
    extra_attrs = data.get("extra_attrs", [])
    # If there are extra attributes
    if extra_attrs:
        # Attributes handler instance
        extra_attr_handler = AttrsHandler(extra_attrs)
        # Validate extra attributes
        extra_attrs, extra_attr_errors = extra_attr_handler.validate_attrs_values(
            del_optional_invalid_attrs=False
        )
        data["extra_attrs"] = extra_attrs
        # if there are errors after extra attributes validation
        if extra_attr_errors:
            # add extra attr errors to the dict with errors
            errors["extra_attrs"] = extra_attr_errors

    # if product is not a parent and product and its variations don't have the same variations
    if not product.get("parent") or product.get("same_images"):
        # then validate img operations
        await validate_image_ops(data.get("image_ops"), errors)

    if product.get("parent"):
        # Check new product variations for errors
        new_variations_errors = await validate_product_variations(data.get("new_variations"),
                                                                  check_images=not product.get("same_images"))

        # if there are errors in new product variations
        if new_variations_errors:
            # Then, add new variation errors to the dict with errors
            errors["new_variations"] = new_variations_errors

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    return {"Sound": "UWU"}
