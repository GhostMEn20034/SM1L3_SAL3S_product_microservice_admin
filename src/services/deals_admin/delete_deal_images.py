from urllib.parse import urlparse

from src.config.settings import S3_BUCKET_NAME
from src.services.upload_images import delete_one_file_in_s3

async def delete_deal_image(image_url: str):
    image_path = urlparse(image_url).path[1:]
    await delete_one_file_in_s3(S3_BUCKET_NAME, image_path)
