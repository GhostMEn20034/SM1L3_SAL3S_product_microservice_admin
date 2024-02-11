from bson import ObjectId

from src.settings import BUCKET_BASE_URL


def create_product_image_name(product_id: ObjectId, image_number: int = 0, extension: str = 'jpg'):
    return f"{BUCKET_BASE_URL}/products/{product_id}_{image_number}.{extension}"