from src.products_admin.utils import AttrsHandler
from src.utils import validate_images, is_list_unique
from typing import List

async def validate_product_images(images, errors):
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

    # list of the SKUs
    skus = []

    for index, variation in enumerate(variations):
        skus.append(variation.get("sku"))
        attr_handler = AttrsHandler(variation.get("attrs"))
        _, attr_errors = attr_handler.validate_attrs_values(del_optional_invalid_attrs=False)
        if attr_errors:
            errors[index] = {"attrs": attr_errors }

        images = variation.get("images")
        image_errors = {}
        if check_images:
            await validate_product_images(images, image_errors)

        if image_errors:
            # set a default value for the index if it does not exist
            errors.setdefault(index, {})
            # update the existing dictionary with the new one
            errors[index].update(image_errors)

    duplicate_sku_index = is_list_unique(skus)

    if duplicate_sku_index:
        errors.setdefault(duplicate_sku_index, {})
        errors[duplicate_sku_index].update({"sku": "SKU must be unique for each variation"})

    return errors
