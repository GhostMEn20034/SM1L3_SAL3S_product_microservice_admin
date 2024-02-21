import asyncio
import base64
from decimal import Decimal
from bson.decimal128 import Decimal128
from typing import Union, List, Optional
from pydantic import ValidationError

from src.config.settings import ALLOWED_IMAGE_TYPE
from src.schemes.url_validator import UrlValidator

async def validate_images(images: Union[str, List[str]], many: bool = False):
    """
    Validates one image or list of images.
    :param images: one image or list of images to validate.
    :param many: Determines whether function should validate one image or many images.
    :return: errors if any
    """
    # dict that stores image errors
    errors = {}

    def check_image_size_and_type(image: str, index):
        """
        A helper function that checks image size and type
        :param image: image for check
        :param index: index that will be assigned as key error in the dict of errors
        """
        # list of errors for current image
        image_errors = []
        # get the image
        encoded_image = image.split(",")[1]
        # decode the image
        decoded_image = base64.b64decode(encoded_image)
        # get type of the file
        file_type = image.split(",")[0].split(";")[0]
        # if file_type is not data:image/jpeg
        if file_type != ALLOWED_IMAGE_TYPE:
            image_errors.append("Only image/jpeg type allowed")

        # get the file size in megabytes
        file_size = round(len(decoded_image) / 1024 ** 2, 2)
        # if file_size is more than 1 MB
        if file_size > 1:
            image_errors.append("The file size exceeds 1 MB")

        # if there are errors for current images, then add these errors to the dict of errors
        if image_errors:
            errors[index] = image_errors
    # if many is True
    if many:
        # Then validate multiple images and return errors
        for index, image in enumerate(images):
            check_image_size_and_type(image, index)

        return errors

    # Otherwise, validate only one image
    check_image_size_and_type(images, 0)
    # return image errors located in "0" key if errors dict is not empty, otherwise return None
    return errors[0] if errors else None

def convert_decimal(dict_item):
    # This function iterates a dictionary looking for types of Decimal and converts them to Decimal128
    # Embedded dictionaries and lists are called recursively.
    if dict_item is None: return None

    for k, v in list(dict_item.items()):
        if isinstance(v, dict):
            convert_decimal(v)
        elif isinstance(v, list):
            for l in v:
                if not isinstance(l, dict):
                    continue
                convert_decimal(l)
        elif isinstance(v, Decimal):
            dict_item[k] = Decimal128(v)

    return dict_item

def is_list_unique(input_list: List) -> Optional[int]:
    duplicate_index = None
    for i in range(len(input_list)):
        for j in range(i + 1, len(input_list)):
            if input_list[i] == input_list[j]:
                duplicate_index = j
                return duplicate_index

    return duplicate_index

def different_dicts(list1: list[dict], list2: list[dict]):
    """
    Compares lists of dictionaries.
    :return: A list of dictionaries from list1 that differ from those in list2.
    """
    differences = []
    for dict1 in list1:
        is_different = True
        for dict2 in list2:
            if dict1 == dict2:
                is_different = False
                break
        if is_different:
            differences.append(dict1)
    return differences

async def get_image_from_base64(base64_str: str) -> bytes:
    """
    Returns image bytes from the base64 encoded string
    """
    # get the image
    encoded_image = base64_str.split(",")[1]
    # decode the image
    decoded_image = base64.b64decode(encoded_image)
    return decoded_image

def async_worker(func, *args, **kwargs):
    """
    Runs asynchronous function in synchronous environment
    Params:
    :param func: async function to execute
    :param args: function's positional arguments
    :param kwargs: function's keyword arguments
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(func(*args, **kwargs))
    return result

def is_valid_url(url: str) -> bool:
    try:
        UrlValidator(url=url)
        return True
    except ValidationError:
        return False
