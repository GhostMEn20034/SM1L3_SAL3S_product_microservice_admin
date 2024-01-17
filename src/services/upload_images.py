import boto3
import io
from bson import ObjectId
from typing import List
from src.utils import get_image_from_base64
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

async def upload_images_single_product(product_id: ObjectId, images: dict) -> dict:
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
        "secondaryImages": secondary_image_urls,
        "sourceProductId": None,
    }}

async def upload_images_many_products(product_ids: List[ObjectId], images: List[dict]):
    """
    Uploads images for many products.
    Use this function if each product has different images.

    Note that count of product IDs and dictionaries with images must be equal.

    :param product_ids: List of IDs of the products.
    :param images: List of product images.
    :return: List of image URLs.
    """
    # if there is no product ids or images or len of the product ids is not equal to the length of image
    if not all((product_ids, images)) or len(product_ids) != len(images):
        # then return empty list
        return []

    # Cache for existing image URLs
    existing_image_urls = {}
    # list of dicts that store image urls
    image_urls_list = []

    for product_id, image in zip(product_ids, images):
        # If product's image dict has sourceProductId with ObjectId type
        # it means that product refers to the existed product,
        # and we just add product_id and image dict to the image_urls_list
        if isinstance(image.get("sourceProductId"), ObjectId):
            # Add to image_urls_list and go to the next iteration
            image_urls_list.append({"product_id": product_id, "images": image})
            continue

        if image.get("sourceProductId") is not None:
            source_product_id = product_ids[image["sourceProductId"]]
            # Check for existing image URLs for the source product
            source_image_urls = existing_image_urls.get(source_product_id)

            if source_image_urls:
                image_urls_list.append(
                    {"product_id": product_id, "images": {**source_image_urls, "sourceProductId": source_product_id}}
                )
            else:
                # Upload images from the actual source image dictionary
                source_images = images[image["sourceProductId"]]  # Retrieve images from the correct source
                source_image_urls = await upload_images_single_product(source_product_id, source_images)
                existing_image_urls[source_product_id] = source_image_urls.get("images", {})
                image_urls_list.extend(
                    [
                        {**source_image_urls, "product_id": source_product_id},
                        {"product_id": product_id,
                         "images": {**source_image_urls.get("images", {}), "sourceProductId": source_product_id}},
                    ]
                )
        else:
            # Check for cached URLs for this product
            cached_urls = existing_image_urls.get(product_id)
            if not cached_urls:
                # Upload images for this unique product
                image_urls = await upload_images_single_product(product_id, image)
                existing_image_urls[product_id] = image_urls.get("images")
                image_urls_list.append({**image_urls, "product_id": product_id})

    return image_urls_list
