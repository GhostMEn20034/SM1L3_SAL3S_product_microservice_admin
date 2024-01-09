from typing import List, Optional, Tuple
import multiprocessing as mp

from src.database import db, client
from src.schemes import PyObjectId
from src.products_admin.utils import remove_product_attrs
from .upload_images import upload_photos_single_product, upload_product_photos


async def insert_product(product_data: dict, session=None) -> PyObjectId:
    """
    Creates one parent product or product that has no children (variations).
    :param product_data: The product data from which the product will be created.
    :param session: If you want to insert product inside the transaction, you need to pass session
    :return: id of the inserted product
    """
    # get base attributes from the product data
    base_attrs = product_data.get("base_attrs", {})

    # get extra attrs from the product data
    # if extra attrs is None, then the value will be an empty list
    extra_attrs = product_data.get("extra_attrs") if product_data.get("extra_attrs") else []

    # form a dictionary with product data which will be inserted into db
    data_to_insert = {
        **base_attrs,
        "parent": product_data.get("parent"), # Is a parent product
        "parent_id": None, # id of parent (For parent product or product without children value is None)
        "for_sale": product_data.get("for_sale"), # is product for sale
        "same_images": product_data.get("same_images"), # Do parent product and product variations have the same images
        "variation_theme":  product_data.get("variation_theme"),  # variation theme
        "is_filterable": product_data.get("is_filterable"), # Are product's attributes can be used in filters?
        "category": product_data.get("category"), # product category
        "attrs":  product_data.get("attrs", []), # main attributes
        "extra_attrs": extra_attrs, # extra attributes
    }

    inserted_product = await db.products.insert_one(data_to_insert, session=session)
    return inserted_product.inserted_id


async def insert_variations(product_data: dict,
                            parent_id: PyObjectId, session=None) -> Tuple[Optional[List[dict]] ,List[PyObjectId]]:
    """
    Creates product variations with the specified data
    :param product_data: The product data from which the product variations will be created.
    :param parent_id: identifier of parent product
    :param session: If you want to insert product variations inside the transaction, you need to pass session
    :return: List of images if same_images is false and List of inserted products' ids
    """
    # get main attributes
    attrs = product_data.get("attrs", [])
    # get product variations
    variations = product_data.get("variations")

    # Do parent product and product variations have the same images
    same_images = product_data.get("same_images")

    # get extra attrs from the product data
    # if extra attrs is None, then the value will be an empty list
    extra_attrs = product_data.get("extra_attrs") if product_data.get("extra_attrs") else []

    # Dict with common product data
    common_data = {
        "parent": False,  # Is a parent product
        "parent_id": parent_id,  # id of parent (For parent product or product without children value is None)
        "for_sale": product_data.get("for_sale"),  # is product for sale
        "same_images": same_images,
        "is_filterable": product_data.get("is_filterable"),  # Are product's attributes can be used in filters?
        "variation_theme": product_data.get("variation_theme"),  # get variation theme
        "category": product_data.get("category"),  # product category
        "extra_attrs": extra_attrs,  # get extra attributes
    }

    if not same_images:
        images_to_upload = [] # images that will be uploaded
        product_variations = []  # product variations data from which the product variations will be created in the db
        for variation in variations:
            variation_attrs = variation.get("attrs")
            # return and remove images from product variation
            variation_images = variation.pop("images", None)
            images_to_upload.append(variation_images)
            data_to_insert = {
                **variation,  # unpack variation's base attributes
                **common_data, # unpack common data for all variations
                "attrs": attrs + variation_attrs,  # concatenate parent attributes and variation attributes
            }
            product_variations.append(data_to_insert)
        inserted_products = await db.products.insert_many(product_variations, session=session)
        inserted_ids: List[PyObjectId] = inserted_products.inserted_ids

        return images_to_upload, inserted_ids

    product_variations = []  # product variations data from which the product variations will be created in the db
    for variation in variations:
        variation_attrs = variation.get("attrs")
        # remove images from the product variation
        variation.pop("images", None)
        data_to_insert = {
            **variation,  # unpack variation's base attributes
            **common_data,  # unpack common data for all variations
            "attrs": attrs + variation_attrs,  # concatenate two arrays
        }
        product_variations.append(data_to_insert)

    inserted_products = await db.products.insert_many(product_variations, session=session)
    inserted_ids: List[PyObjectId] = inserted_products.inserted_ids
    return None ,inserted_ids


async def insert_product_to_db(product_data: dict):
    """
    Inserts product and product variations to the database.

    :param product_data: product data such as attributes,
    variations and so on (see src/products/schemes.py and src/products_admin/schemes.py).
    :return: parent id and list of inserted products' ids OR single product id and None
    """
    has_variations = product_data.get("has_variations", False)
    same_images = product_data.get("same_images", True)

    # If product has variations
    if has_variations:
        async with await client.start_session() as session:
            async with session.start_transaction():
                # Get variation theme options
                var_theme_options = product_data.get("variation_theme", {}).get("options", [])

                def set_optional(elem):
                    """
                    Helper function to set property "optional"
                    to False
                    """
                    # copy the element to avoid mutating the original list
                    new_elem = elem.copy()
                    # set the "optional" property to True
                    new_elem["optional"] = False
                    # return the new element
                    return new_elem

                product_data["attrs"] = list(map(set_optional, product_data["attrs"]))

                for variation in product_data.get("variations"):
                    variation["attrs"] = list(map(set_optional, variation["attrs"]))

                # create a parent product
                parent = await insert_product(
                    {
                        "base_attrs": product_data.get("base_attrs"),
                        "attrs": product_data.get("attrs"),
                        "extra_attrs": product_data.get("extra_attrs"),
                        "parent": True,
                        "is_filterable": False,
                        "for_sale": False,
                        "category": product_data.get("category"),
                        "variation_theme": product_data.get("variation_theme"),
                        "same_images": same_images
                    },
                    session=session
                )
                # stores all variation theme field codes
                field_codes = []
                # get all variation theme field codes
                for option in var_theme_options:
                    field_codes.extend(option.get("field_codes", []))

                # remove parent's attributes
                product_data["attrs"] = await remove_product_attrs(product_data["attrs"], field_codes)

                # create product variations
                images_to_upload, product_variations = await insert_variations(
                    {
                        "attrs": product_data.get("attrs"),
                        "extra_attrs": product_data.get("extra_attrs"),
                        "for_sale": True,
                        "is_filterable": product_data.get("is_filterable", False),
                        "category": product_data.get("category"),
                        "variation_theme": product_data.get("variation_theme"),
                        "same_images": same_images,
                        "variations": product_data.get("variations")
                    },
                    parent,
                    session=session
                )

                # Upload photos in the another process to reduce response time
                mp.Process(
                    target=upload_product_photos,
                    name="upload_images_multiple_prods",
                    args=(
                        {"same_images": same_images, "images": product_data.get("images")},
                        parent,
                        product_variations,
                        images_to_upload
                    )
                ).start()
                # return parent id and list of inserted products' ids
                return parent, product_variations

    # create a single product
    single_product = await insert_product(
        {
            "base_attrs": product_data.get("base_attrs"),
            "attrs": product_data.get("attrs"),
            "extra_attrs": product_data.get("extra_attrs"),
            "parent": False,
            "is_filterable": product_data.get("is_filterable", False),
            "for_sale": True,
            "category": product_data.get("category"),
            "variation_theme": product_data.get("variation_theme"),
            "same_images": same_images
        }
    )

    # Upload photos in the another process to reduce response time
    mp.Process(
        target=upload_photos_single_product,
        name="upload_photos_single_prod",
        args=(
            single_product,
            {"images": product_data.get("images")}
        )
    ).start()

    return single_product, None
