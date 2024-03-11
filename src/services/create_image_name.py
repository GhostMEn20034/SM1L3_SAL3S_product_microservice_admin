from bson import ObjectId

from src.config.settings import CDN_HOST_NAME


def create_product_image_name(product_id: ObjectId, image_number: int = 0, extension: str = 'jpg'):
    return f"{CDN_HOST_NAME}/products/{product_id}_{image_number}.{extension}"
