from typing import Union, Optional

from pydantic import BaseModel, Field, constr

from src.schemes.py_object_id import PyObjectId


class FacetBase(BaseModel):
    """
    Model that represents base facet fields
    used in the detail facet representation and in the list representation
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: str
    name: str
    type: str
    optional: bool
    show_in_filters: bool


class RangeValue(BaseModel):
    """
    Represents range of first number (gteq) inclusive and the second number (ltn) exclusive
    """
    gteq: Union[float, int] # Greater than equal value
    ltn: Optional[Union[float, int]] # Less than value
    display_name: constr(min_length=1) # Display Name - string representation of
    # range of gteq inclusive and ltn exclusive
