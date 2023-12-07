from typing import List
from decimal import Decimal
from src.database import db
from src.schemes import PyObjectId


class AttrsHandler:
    """
    Used to handle product attributes.
    For example, you can use this class for validation product attrs.
    Or you can use it to convert product attrs values on displayable values.
    """

    def __init__(self, attrs: List[dict]):
        self.attrs = attrs

    def validate_attrs_values(self, del_optional_invalid_attrs: bool = True):
        """
        Method for validation product attribute values.
        Suppose one of the attributes is bivariate (it should have value [value0, value1]). If value written
        by the user will be invalid, method will add error to the list of errors.

        :param del_optional_invalid_attrs: determines whether to delete optional invalid attributes

        :return: validated list of attributes and errors, if any.
        """
        errors = {} # list of attribute errors
        attrs_to_delete = [] # list of attribute indexes to remove

        def append_error_or_delete_attr(attr: dict, message: str, attr_index: int):
            """
            A helper function that appends error to the list of errors if attr is not optional
            or if del_optional_invalid_attrs is False. Or it's appends index to the list of attributes to delete

            :param attr: dictionary that stores data about product attribute.
            :param message: error message.
            :param attr_index: attribute index
            """
            if not attr.get("optional") or not del_optional_invalid_attrs:
                error_msg = f"{attr.get('name')} {message}"

                errors[attr.get("code")] = error_msg
            else:
                attrs_to_delete.append(attr_index)


        for index, attr in enumerate(self.attrs):
            match attr.get("type"):
                case "string":
                    # if attr value is not str or str is empty
                    if not isinstance(attr.get("value"), str) or len(attr.get("value")) < 1:
                        # if attr is optional, then remove attr from an array, otherwise add error to the list of errors
                        append_error_or_delete_attr(attr, "must have at least 1 symbol", index)

                case "decimal" | "integer":
                    # If attr value is not int or float or decimal
                    if not isinstance(attr.get("value"), (int, float, Decimal)):
                        # if attr is optional, then remove attr from an array, otherwise add error to the list of errors
                        append_error_or_delete_attr(attr, "must be integer or decimal number", index)

                case "list":
                    # if attr value is not list or value is not list or list is empty
                    if not attr.get("value") or not isinstance(attr.get("value"), list):
                        # if attr is optional, then remove attr from an array, otherwise add error to the list of errors
                        append_error_or_delete_attr(attr, "must be list", index)

                case "bivariate":
                    # if there's no value or list is empty or value is not a list or length of list is not 2
                    if not attr.get("value") or not isinstance(attr.get("value"), list) or len(attr.get("value")) != 2:
                        # if attr is optional, then remove attr from an array, otherwise add error to the list of errors
                        append_error_or_delete_attr(attr, "must be bivariate", index)

                case "trivariate":
                    # if there's no value or list is empty or value is not a list or length of list is not 3
                    if not attr.get("value") or not isinstance(attr.get("value"), list) or len(attr.get("value")) != 3:
                        # if attr is optional, then remove attr from an array, otherwise add error to the list of errors
                        append_error_or_delete_attr(attr, "must be trivariate", index)

        # if list of attribute indexes is not empty, then remove attributes with the specified indexes from the list
        if attrs_to_delete:
            # Use a list comprehension to keep only the elements that are not in attrs_to_delete
            self.attrs = [self.attrs[i] for i in range(len(self.attrs)) if i not in attrs_to_delete]

        return self.attrs, errors


async def remove_parent_attrs(attrs: List[dict], variation_theme: PyObjectId) -> List[dict]:
    """
    Removes attributes if attribute code in the list of variation theme field codes
    """
    # Query a variation theme from db
    var_theme_data = await db.variation_themes.find_one({"_id": variation_theme})
    # stores all variation theme field codes
    field_codes = []

    # get all variation theme field codes
    for var_theme_filter in var_theme_data.get("filters", []):
        field_codes.extend(var_theme_filter.get("field_codes"))

    # filter product attributes. If attribute code is equal to one of variation theme field codes,
    # then remove attribute from list
    filtered_attrs = filter(lambda attr: attr["code"] not in field_codes, attrs)

    return list(filtered_attrs)
