from src.apps.events.schemes.create import CreateEvent
from src.apps.events.schemes.update import UpdateEvent
from src.utils import validate_images


class EventValidatorCreate:
    def __init__(self, event: CreateEvent):
        self.event = event
        self.errors = {}

    async def validate(self) -> dict:
        image_errors = await validate_images(self.event.image)
        if image_errors:
            self.errors['image'] = image_errors

        return self.errors


class EventValidatorUpdate:
    def __init__(self, event: UpdateEvent):
        self.event = event
        self.errors = {}

    async def validate(self) -> dict:
        image_errors = await validate_images(self.event.image)
        if image_errors:
            self.errors['image'] = image_errors

        return self.errors