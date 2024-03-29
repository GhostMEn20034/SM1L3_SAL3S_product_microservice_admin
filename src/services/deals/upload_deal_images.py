import io

from src.config.settings import S3_BUCKET_NAME, CDN_HOST_NAME
from src.services.upload_images import upload_file_to_s3
from src.utils import get_image_from_base64

async def upload_deal_image(image: str, image_name: str):
    """
    :param image: image encoded in base64 string
    :param image_name: image name (with extension) without folder
    """
    # decode base64 string and extract image
    new_image = await get_image_from_base64(image)
    new_image_bytes_io = io.BytesIO(new_image)

    full_image_name = "deals/" + image_name
    await upload_file_to_s3(full_image_name, new_image_bytes_io, S3_BUCKET_NAME)
    image_url = CDN_HOST_NAME + "/" + full_image_name
    return image_url

