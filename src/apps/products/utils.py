from typing import List
from decimal import Decimal

class AttrsHandler:
    """
    Used to handle product attributes.
    You can use this class for validation product attrs.
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

        # If there are no product attributes, then return empty list and empty error dict
        if not self.attrs:
            return [], errors

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
                    # if attr value is not list or list is empty
                    if not attr.get("value") or not isinstance(attr.get("value"), list):
                        # if attr is optional, then remove attr from an array, otherwise add error to the list of errors
                        append_error_or_delete_attr(attr, "must be a list and have at least one item", index)

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


async def remove_product_attrs(attrs: List[dict], field_codes: List[str]) -> List[dict]:
    """
    Removes attributes if attribute code in the list of variation theme field codes
    """
    # filter product attributes. If attribute code is equal to one in field codes,
    # then remove attribute from list
    filtered_attrs = filter(lambda attr: attr["code"] not in field_codes, attrs)
    return list(filtered_attrs)

async def set_attr_non_optional(attrs: List[dict]) ->  List[dict]:
    """
    Set "optional" property to False in all product attributes
    """
    return list(map(lambda attr: {**attr, "optional": False}, attrs))


def form_data_to_update(product_data: dict, parent: bool):
    """
    Returns only the necessary data to update the product.
    :param product_data: All product data to update
    :param parent: Whether a product is a parent.
    """
    data_to_update = {
        **product_data.get("base_attrs", {}),
        "attrs": product_data.get("attrs", []),
        "extra_attrs": product_data.get("extra_attrs", []),
        "search_terms": product_data.get("search_terms", []),
    }

    if not parent:
        data_to_update.update({
           "for_sale": product_data.get("for_sale"),
           "is_filterable": product_data.get("is_filterable"),
        })

    return data_to_update

async def get_var_theme_field_codes(variation_theme: dict):
    """
    Return Variation theme field codes
    """
    # Get variation theme options
    var_theme_options = variation_theme.get("options", [])
    # stores all variation theme field codes
    field_codes = []
    # get all variation theme field codes
    for option in var_theme_options:
        field_codes.extend(option.get("field_codes", []))

    return field_codes
