from src.deals_admin.schemes.create import CreateDealSchema
from src.deals_admin.schemes.update import UpdateDealSchema
from src.utils import validate_images, is_valid_url


class DealValidatorCreate:
    def __init__(self, deal: CreateDealSchema):
        self.deal = deal
        self.errors = {}

    async def validate(self) -> dict:
        image_errors = await validate_images(self.deal.image)
        if image_errors:
            self.errors['image'] = image_errors

        return self.errors


class DealValidatorUpdate:
    def __init__(self, deal: UpdateDealSchema):
        self.deal = deal
        self.errors = {}

    async def validate(self) -> dict:
        # if there's an image value and it is not valid url
        if not is_valid_url(self.deal.image) and self.deal.image is not None:
            image_errors = await validate_images(self.deal.image)
            if image_errors:
                self.errors['image'] = image_errors

        return self.errors