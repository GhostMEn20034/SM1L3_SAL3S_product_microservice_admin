from pydantic import BaseModel, constr


class CreateSearchTerm(BaseModel):
    name: constr(min_length=1, strip_whitespace=True, to_lower=True)
