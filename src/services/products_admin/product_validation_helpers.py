from typing import List
from bson.objectid import ObjectId
from src.apps.products_admin.utils import AttrsHandler
from src.utils import validate_images, is_list_unique


async def validate_product_images(images, errors):
    """
    Validates product images
    FUNCTION DO NOT RETURN ERRORS EXPLICITLY.
    IT MUTATES ERRORS DICT PASSED TO THE FUNCTION
    """
    main_image_errors = await validate_images(images.get("main"))
    secondary_images = images.get("secondaryImages")
    secondary_images_errors = await validate_images(secondary_images, many=True) if secondary_images else None
    # if there are images errors
    if main_image_errors or secondary_images_errors:
        errors["images"] = {
            "main": main_image_errors if main_image_errors else None,
        }
        if secondary_images_errors:
            errors["images"]["secondaryImages"] = secondary_images_errors

async def validate_product_variations(variations: List[dict], check_images: bool):
    """
    Validates product variation attrs and images.

    :param variations: Product variation list.
    :param check_images: Determines whether to validate product images

    :return: errors

    """
    errors = {}

    if len(variations) == 0:
        return errors

    # list of the SKUs
    skus = []

    for index, variation in enumerate(variations):
        skus.append(variation.get("sku"))
        attr_handler = AttrsHandler(variation.get("attrs"))
        # Validate variation attributes
        _, attr_errors = attr_handler.validate_attrs_values(del_optional_invalid_attrs=False)
        if attr_errors:
            errors[index] = {"attrs": attr_errors }

        # get variation images
        images = variation.get("images")
        image_errors = {}
        # if check_images is True and sourceProductId is not ObjectId or int
        if check_images and not isinstance(images.get("sourceProductId"), (int, ObjectId)):
            # then validate images
            await validate_product_images(images, image_errors)

        # if there are image errors
        if image_errors:
            # set a default value for the index if it does not exist
            errors.setdefault(index, {})
            # update the existing dictionary with the new one
            errors[index].update(image_errors)

    duplicate_sku_index = is_list_unique(skus)

    # if there's a sku duplicate
    if duplicate_sku_index:
        # then include error that SKU must be unique for each variation
        errors.setdefault(duplicate_sku_index, {})
        errors[duplicate_sku_index].update({"sku": "SKU must be unique for each variation"})

    return errors

async def validate_image_ops(image_ops: dict, errors: dict):
    """
    Validate images that will be used for specified operations
    FUNCTION DO NOT RETURN ERRORS EXPLICITLY.
    IT MUTATES ERRORS DICT PASSED TO THE FUNCTION
    """
    # If there are images to add
    if image_ops.get("add"):
        # Validate list of images to add
        images_add_errors = await validate_images(image_ops.get("add"), many=True)
        # IF there are errors for images to add
        if images_add_errors:
            # Then, add these errors to the error dict
            errors.setdefault("image_ops", {})["add"] = images_add_errors

    # if there is a new main image in replace operation
    if image_ops.get("replace").get("main"):
        # Validate new main image
        main_image_errors = await validate_images(image_ops.get("replace").get("main"))
        # IF there are errors for a new main image
        if main_image_errors:
            # Then, add these errors to the error dict
            errors.setdefault("image_ops", {}).setdefault("replace", {})["main"] = main_image_errors

    # if there are new secondary images in replace operation
    if image_ops.get("replace").get("secondaryImages"):
        # Validate new secondary images
        for image in image_ops.get("replace").get("secondaryImages"):
            secondary_image_errors = await validate_images(image.get("newImg"))
            # IF there are errors for images to replace
            if secondary_image_errors:
                # Then, add these errors to the error dict
                (errors.setdefault("image_ops", {}).setdefault("replace", {})
                 .setdefault("secondaryImages", {}).update(
                    {image.get("index", 0): secondary_image_errors}
                ))

