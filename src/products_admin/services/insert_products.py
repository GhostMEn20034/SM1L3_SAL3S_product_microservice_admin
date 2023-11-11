from typing import List, Optional, Tuple
from fastapi import BackgroundTasks

from src.database import db, client
from src.schemes import PyObjectId
from src.services.upload_images import upload_imgs_single_prod, upload_imgs_many_prods, update_image_links
from src.settings import BUCKET_BASE_URL
from src.products_admin.utils import remove_parent_attrs


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
        "variation_theme":  product_data.get("variation_theme"),  # variation theme id
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
                "parent": False, # Is a parent product
                "parent_id": parent_id, # id of parent (For parent product or product without children value is None)
                "for_sale": product_data.get("for_sale"), # is product for sale
                "same_images": same_images,
                "variation_theme": product_data.get("variation_theme"), # variation theme id
                "category": product_data.get("category"), # product category
                "attrs": attrs + variation_attrs,  # concatenate parent attributes and variation attributes
                "extra_attrs": extra_attrs, # extra attributes
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
            "parent": False,  # Is a parent product
            "parent_id": parent_id, # id of parent (For parent product or product without children value is None)
            "for_sale":  product_data.get("for_sale"), # is product for sale
            "same_images": same_images,
            "variation_theme": product_data.get("variation_theme"), # get variation theme id
            "category": product_data.get("category"), # product category
            "attrs": attrs + variation_attrs,  # concatenate two arrays
            "extra_attrs": extra_attrs, # get extra attributes
        }
        product_variations.append(data_to_insert)

    inserted_products = await db.products.insert_many(product_variations, session=session)
    inserted_ids: List[PyObjectId] = inserted_products.inserted_ids
    return None ,inserted_ids


async def insert_product_to_db(product_data: dict, background_tasks: BackgroundTasks):
    """
    Inserts product and product variations to the database.

    :param product_data: product data such as attributes,
    variations and so on (see src/products/schemes.py and src/products_admin/schemes.py).
    :param background_tasks: FASTAPI BackgroundTasks object
    :return: parent id and list of inserted products' ids OR single product id and None
    """
    has_variations = product_data.get("has_variations", False)
    same_images = product_data.get("same_images", True)

    # If product has variations
    if has_variations:
        async with await client.start_session() as session:
            async with session.start_transaction():
                # create a parent product
                parent = await insert_product(
                    {
                        "base_attrs": product_data.get("base_attrs"),
                        "attrs": product_data.get("attrs"),
                        "extra_attrs": product_data.get("extra_attrs"),
                        "parent": True,
                        "for_sale": False,
                        "category": product_data.get("category"),
                        "variation_theme": product_data.get("variation_theme"),
                        "same_images": same_images
                    },
                    session=session
                )

                product_data["attrs"] = await remove_parent_attrs(product_data["attrs"], product_data["variation_theme"])
                # create product variations
                images_to_upload, product_variations = await insert_variations(
                    {
                        "attrs": product_data.get("attrs"),
                        "extra_attrs": product_data.get("extra_attrs"),
                        "for_sale": True,
                        "category": product_data.get("category"),
                        "variation_theme": product_data.get("variation_theme"),
                        "same_images": same_images,
                        "variations": product_data.get("variations")
                    },
                    parent,
                    session=session
                )

                async def upload_product_photos():
                    """
                    A helper function that uploads product photos to the storage and updates image URLs in the db.
                    """
                    # if same_images if False
                    if not same_images:
                        # Update images URLs for the parent product
                        await update_image_links(parent,
                                                 {
                                                  "main": f"{BUCKET_BASE_URL}/products/{product_variations[0]}_0.jpg",
                                                  "secondaryImages": None
                                                 },
                                                 )
                        # Upload product images to S3 storage
                        image_urls_list = await upload_imgs_many_prods(product_variations, images_to_upload)
                        # Update images URLs for the variations
                        await update_image_links(product_variations, [i.get("images") for i in image_urls_list])
                    else:
                        # Upload the same product images for all variations to S3 storage
                        image_urls = await upload_imgs_single_prod(parent, product_data.get("images"))
                        # Update the same images URLs for the variations
                        await update_image_links([parent, *product_variations], image_urls.get("images"),
                                                 same_images=True)

                # Upload photos in the background to reduce response time
                background_tasks.add_task(upload_product_photos)
                # return parent id and list of inserted products' ids
                return parent, product_variations

    # create a single product
    single_product = await insert_product(
        {
            "base_attrs": product_data.get("base_attrs"),
            "attrs": product_data.get("attrs"),
            "extra_attrs": product_data.get("extra_attrs"),
            "parent": False,
            "for_sale": True,
            "category": product_data.get("category"),
            "variation_theme": product_data.get("variation_theme"),
            "same_images": same_images
        }
    )

    async def upload_photos_single_product():
        """
        A helper function that uploads photos for a single product to the storage and updates image URLs in the db.
        """
        # Upload images for a single product to S3 storage
        image_urls = await upload_imgs_single_prod(single_product, product_data.get("images"))
        # Update the same images URLs for the variations
        await update_image_links(single_product, image_urls.get("images"))

    background_tasks.add_task(upload_photos_single_product)

    return single_product, None
