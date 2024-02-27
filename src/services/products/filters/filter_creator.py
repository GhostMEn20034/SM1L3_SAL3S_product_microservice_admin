from src.apps.products.schemes.get import ProductSearchFilters

class ProductsFilterCreatorAdmin:
    """
    Responsible for creating filters in admin panel for products
    """
    @staticmethod
    async def generate_search_product_filters(filters: ProductSearchFilters) -> dict:
        filter_dict: dict = filters.dict(exclude_none=True, exclude_defaults=True)
        filter_dict = {k:v for k, v in filter_dict.items() if v}
        if filter_dict.get('category'):
            filter_dict['category'] = {'$in': filter_dict['category']}

        return filter_dict
