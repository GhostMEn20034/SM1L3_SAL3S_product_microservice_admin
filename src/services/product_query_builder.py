class ProductQueryBuilder:
    """
    Responsible for building queries for product entity
    """
    async def _form_attr_update_expression(self, attr: dict, index: int ,identifier_name: str) -> dict:
        """
        Forms attribute update expression
        """
        value = attr["value"]
        unit = attr["unit"]
        group = attr["group"]
        return {
            f"attrs.$[{identifier_name}{index}].value": value,
            f"attrs.$[{identifier_name}{index}].unit": unit,
            f"attrs.$[{identifier_name}{index}].group": group,
        }

    async def _form_attr_array_filters(self, attr: dict, index: int, identifier_name: str) -> dict:
        """
        Forms attribute array filters to define which attributes must be updated
        """
        code = attr["code"]
        return {f"{identifier_name}{index}.code": code}

    async def build_update_variations_attrs(self, attrs: list[dict], identifier_name="elem"):
        """
        Returns data for set operator and array filters to identify which attributes need to be updated.
        """
        array_filters = []
        set_operator_data = {}
        for index, attr in enumerate(attrs):
            update_expression: dict = await self._form_attr_update_expression(attr, index, identifier_name)
            set_operator_data.update(update_expression)
            array_filter: dict = await self._form_attr_array_filters(attr, index, identifier_name)
            array_filters.append(array_filter)

        return set_operator_data, array_filters
