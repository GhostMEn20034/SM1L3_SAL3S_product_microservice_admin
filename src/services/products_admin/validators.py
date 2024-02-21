from src.apps.products_admin.schemes.create import CreateProduct
from src.apps.products_admin.schemes.update import UpdateProduct, ExtraProductDataUpdate
from src.services.products_admin.product_validation_helpers import (
    validate_product_images, validate_product_variations, validate_image_ops
)
from src.apps.products_admin.repository import ProductAdminRepository
from src.apps.products_admin.utils import AttrsHandler


class ProductValidatorBase:
    """
    Ensures that the product meets the business requirements
    """

    def __init__(self, product: dict, product_repo: ProductAdminRepository):
        self.product = product
        self.errors = {}
        self.product_repo = product_repo

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

    async def _check_if_skus_exist(self, skus: list[str]):
        """
        Check whether product skus exists in db.
        :return: List of skus that exist
        """
        existed_skus = []
        products = await self.product_repo.get_product_list({"sku": {"$in": skus}},
                                                            {"_id": 0, "sku": 1})
        for product in products:
            existed_skus.append(product.get("sku"))

        if existed_skus:
            error_message = f"SKUs: {', '.join(existed_skus)} already exist!"
            self.errors["existed_skus"] = error_message


class ProductValidatorCreate(ProductValidatorBase):
    """
    Ensures that the product creation data meets the business requirements
    """

    def __init__(self, product: CreateProduct, product_repo: ProductAdminRepository):
        super().__init__(product.dict(), product_repo)

    async def validate(self):
        """
        Validates the product creation data.
        :return: Validated product data and dictionary with errors
        """
        self._validate_product_attrs()
        self._validate_product_attrs("extra_attrs", False)

        skus = []
        # If there are images in product_data
        if images := self.product.get("images"):
            # Then, validate images in product_data
            await validate_product_images(images, self.errors)
        # if product has variations
        if (has_variations := self.product.get("has_variations")) \
                and (variations := self.product.get("variations")):
            variation_skus = list(map(lambda product: product.get("sku"), variations))
            skus.extend(variation_skus)

            check_images = has_variations and not self.product.get("same_images")
            # Check product variations for errors
            variation_errors = await validate_product_variations(variations, check_images)
            # if there are errors in product variations
            if variation_errors:
                # Then, add variation errors to the dict with errors
                self.errors["variations"] = variation_errors

        skus.append(self.product.get("base_attrs", {}).get("sku"))
        await self._check_if_skus_exist(skus)

        return self.product, self.errors


class ProductValidatorUpdate(ProductValidatorBase):
    """
    Ensures that the product update data meets the business requirements
    """

    def __init__(self, product: UpdateProduct, extra_data: ExtraProductDataUpdate,
                 product_repo: ProductAdminRepository):
        super().__init__(product.dict(by_alias=True), product_repo)
        self.extra_data = extra_data

    async def validate(self):
        """
        Validates the product creation data.
        :return: Validated product data and dictionary with errors
        """
        self._validate_product_attrs()
        self._validate_product_attrs("extra_attrs", False)

        skus = []
        # if product is not a parent or product and its variations don't have the same images
        if not self.extra_data.get("parent") or self.extra_data.get("same_images"):
            # then validate img operations
            await validate_image_ops(self.product.get("image_ops"), self.errors)

        if self.extra_data.get("parent"):
            # old_variations_skus = list(map(lambda product: product.get("sku"), self.product.get("old_variations")))
            # skus.extend(old_variations_skus)
            new_variations_skus = list(map(lambda product: product.get("sku"), self.product.get("new_variations")))
            skus.extend(new_variations_skus)

            # Check new product variations for errors
            new_variations_errors = await validate_product_variations(self.product.get("new_variations"),
                                                                      check_images=not self.extra_data.get(
                                                                          "same_images"))
            # if there are errors in new product variations
            if new_variations_errors:
                # Then, add new variation errors to the dict with errors
                self.errors["new_variations"] = new_variations_errors

        # skus.append(self.product.get("base_attrs", {}).get("sku"))
        await self._check_if_skus_exist(skus)
        return self.product, self.errors
