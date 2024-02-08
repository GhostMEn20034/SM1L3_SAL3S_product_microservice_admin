from pydantic import AnyUrl, BaseModel


class UrlValidator(BaseModel):
    url: AnyUrl