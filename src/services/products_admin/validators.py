from src.products_admin.schemes.create import CreateProduct
from src.products_admin.schemes.update import UpdateProduct, ExtraProductDataUpdate
from src.services.products_admin.product_validation_helpers import (
    validate_product_images, validate_product_variations, validate_image_ops
)
from src.products_admin.utils import AttrsHandler


class ProductValidatorBase:
    """
    Ensures that the product meets the business requirements
    """

    def __init__(self, product: dict):
        self.product = product
        self.errors = {}

    async def validate(self):
        raise NotImplementedError

    def _validate_product_attrs(self, keyname: str = "attrs", del_optional_invalid_attrs: bool = True):
        """
        sets validated attributes to the product dict
        and adds errors to the errors dict.
        :param keyname: the name of the key for product attributes (specs) in the product dict
        :param del_optional_invalid_attrs: determines whether to delete optional invalid attributes
        """
        attr_handler = AttrsHandler(self.product.get(keyname, []))
        # Validate attributes
        validated_attrs, attr_errors = attr_handler.validate_attrs_values(del_optional_invalid_attrs)
        # Assign validated attributes to the product
        self.product[keyname] = validated_attrs
        if attr_errors:
            # if there are attribute errors, then add attr errors to the dictionary with errors
            self.errors[keyname] = attr_errors


class ProductValidatorCreate(ProductValidatorBase):
    """
    Ensures that the product creation data meets the business requirements
    """
    def __init__(self, product: CreateProduct):
        super().__init__(product.dict())

    async def validate(self):
        """
        Validates the product creation data.
        :return: Validated product data and dictionary with errors
        """
        self._validate_product_attrs()
        self._validate_product_attrs("extra_attrs", False)
        # If there are images in product_data
        if images := self.product.get("images"):
            # Then, validate images in product_data
            await validate_product_images(images, self.errors)
        # if product has variations
        if (has_variations := self.product.get("has_variations")) \
                and (variations := self.product.get("variations")):
            check_images = has_variations and not self.product.get("same_images")
            # Check product variations for errors
            variation_errors = await validate_product_variations(variations, check_images)
            # if there are errors in product variations
            if variation_errors:
                # Then, add variation errors to the dict with errors
                self.errors["variations"] = variation_errors

        return self.product, self.errors


class ProductValidatorUpdate(ProductValidatorBase):
    """
    Ensures that the product update data meets the business requirements
    """
    def __init__(self, product: UpdateProduct, extra_data: ExtraProductDataUpdate):
        super().__init__(product.dict(by_alias=True))
        self.extra_data = extra_data

    async def validate(self):
        """
        Validates the product creation data.
        :return: Validated product data and dictionary with errors
        """
        self._validate_product_attrs()
        self._validate_product_attrs("extra_attrs", False)

        # if product is not a parent or product and its variations don't have the same variations
        if not self.extra_data.get("parent") or self.extra_data.get("same_images"):
            # then validate img operations
            await validate_image_ops(self.product.get("image_ops"), self.errors)

        if self.extra_data.get("parent"):
            # Check new product variations for errors
            new_variations_errors = await validate_product_variations(self.product.get("new_variations"),
                                                                      check_images=not self.extra_data.get("same_images"))
            # if there are errors in new product variations
            if new_variations_errors:
                # Then, add new variation errors to the dict with errors
                self.errors["new_variations"] = new_variations_errors

        return self.product, self.errors
