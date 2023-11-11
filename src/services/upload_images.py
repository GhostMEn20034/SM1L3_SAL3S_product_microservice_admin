import boto3
import io
from src.schemes import PyObjectId
from typing import List, Union
from src.utils import get_image_from_base64
from src.database import db
from src.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, BUCKET_BASE_URL


async def upload_image(key: str, bytes_io: io.BytesIO, bucket_name: str):
    """
    Uploads image to the amazon s3 storage.
    :param key: file name.
    :param bytes_io: file in the form of bytes.
    :param bucket_name: Name of the s3 bucket.
    """
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.upload_fileobj(bytes_io, bucket_name, key, ExtraArgs={"ContentType": "image/jpeg"})

async def upload_imgs_single_prod(product_id: PyObjectId, images: dict) -> dict:
    """
    Uploads images for a single product.
    Also, this function can be used to upload the same images for many products.
    :param product_id: ID of a product. Used to form an image name.
    :param images: dict that stores the main image and secondary images.
    :return: dictionary with product_id and image URLs
    """
    # get bytes from the base64 encoded string
    main_image = await get_image_from_base64(images.get("main"))

    # create bytes io object for the main image
    main_image_bytes_io = io.BytesIO(main_image)

    main_image_name = f"products/{product_id}_0.jpg"

    # stores list of URLs of the secondary images if images.secondaryImages is not None
    secondary_image_urls = None

    # upload image to the amazon s3
    await upload_image(main_image_name, main_image_bytes_io, S3_BUCKET_NAME)

    # URL of the uploaded main image
    main_image_url = BUCKET_BASE_URL + "/" + main_image_name

    # check if there are secondary images
    if secondary_images := images.get("secondaryImages"):
        secondary_image_urls = []
        for index ,secondary_image in enumerate(secondary_images):
            secondary_image_name = f"products/{product_id}_{index + 1}.jpg"
            # get bytes from the base64 encoded string
            decoded_secondary_image = await get_image_from_base64(secondary_image)
            # create bytes io object for the secondary image
            secondary_image_bytes_io = io.BytesIO(decoded_secondary_image)
            # upload image to the amazon s3
            await upload_image(secondary_image_name, secondary_image_bytes_io, S3_BUCKET_NAME)
            # URL of the secondary image
            secondary_image_url = BUCKET_BASE_URL + "/" + secondary_image_name
            secondary_image_urls.append(secondary_image_url)

    return {"product_id": product_id, "images": {
        "main": main_image_url,
        "secondaryImages": secondary_image_urls
    }}

async def upload_imgs_many_prods(product_ids: List[PyObjectId], images: List[dict]):
    """
    Uploads images for many products.
    Use this function if each product has different images.

    Note that count of product IDs and dictionaries with images must be equal.

    :param product_ids: List of IDs of the products.
    :param images: List of product images.
    :return: List of image URLs.
    """
    # if there is no product ids or images or len of the product ids is not equal to the length of image
    if not product_ids or not images or len(product_ids) != len(images):
        # then return empty list
        return []

    # list of dicts that store image urls
    image_urls_list = []

    for product_id, image in zip(product_ids, images):
        # upload images and get their URLs
        image_urls = await upload_imgs_single_prod(product_id, image)
        image_urls_list.append(image_urls)

    return image_urls_list





async def update_image_links(product_ids: Union[List[PyObjectId], PyObjectId], images: Union[List[dict], dict],
                             same_images: bool = False):
    """
    Updates image links in products.
    :param product_ids: List of ObjectID or ObjectID. Products where image links will be updated.
    :param images: List of dicts or dict. Image links that will be inserted into the products.
    :param same_images: defines whether function should upload the same images to the products
    """
    # check if the input is a single product id or a list of product ids
    if isinstance(product_ids, list):
        # check if the same_images parameter is True
        if same_images:
            # use the update_many method with the $in operator to update the same images for the products in
            # the product_ids list
            await db.products.update_many(
                {"_id": {"$in": product_ids}},
                {"$set": {"images": images}}
            )
        else:
            # loop through the product ids and images
            for product_id, image in zip(product_ids, images):
                # use the update_one method to update the image names for each product
                await db.products.update_one(
                    {"_id": product_id},
                    {"$set": {"images": image}}
                )
    else:
        # use the update_one method to update the image names for the single product
        await db.products.update_one(
            {"_id": product_ids},
            {"$set": {"images": images}}
        )
