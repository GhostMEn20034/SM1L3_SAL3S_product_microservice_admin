from .base import SynonymBaseModel

class SynonymCreate(SynonymBaseModel):

    class Config:
        use_enum_values = True
