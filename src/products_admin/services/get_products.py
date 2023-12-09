from math import ceil
from src.database import db
from src.schemes import PyObjectId


async def get_product_list(page: int, page_size: int) -> dict:
    """
    Returns product list and count of pages.

    :param page: page number. Suppose for each page you have 5 items. If the page number is 1,
    then db will return only first 5 items. If the page number is 2, then the database will skip the first 5 items,
    and return 5 items after the previous 5 items.
    :param page_size: count of items per page.
    """

    # product fields that will be returned by the db
    product_projection = {
        "name": 1,
        "price": 1,
        "for_sale": 1,
        "parent": 1
    }

    pipeline = [
        {
            # Match the documents that have either parent: True or parent_id: null
            "$match": {
                "$or": [
                    {"parent": True},
                    {"parent_id": None}
                ]
            }
        },
        {
            # Process a multiple pipelines within a single stage on the same set of data
            "$facet": {
                # List of products
                "items": [
                    {
                        # Lookup the documents that have the same parent_id as the _id of the parent document
                        "$lookup": {
                            "from": "products",
                            "localField": "_id",
                            "foreignField": "parent_id",
                            "pipeline": [
                                {
                                    "$project": {
                                        **product_projection,
                                        # Add a tax field, for each joined product
                                        "tax": {"$round": [{"$multiply": ["$price", "$tax_rate"]}, 2]}
                                    }
                                }
                            ],
                            "as": "variations"
                        }
                    },
                    {
                        "$project": {
                            "tax": {"$round": [{"$multiply": ["$price", "$tax_rate"]}, 2]},
                            **product_projection,
                            "variations": 1,
                        }
                    },
                    {
                        "$skip": (page - 1) * page_size
                    },
                    {
                        "$limit": page_size
                    },
                ],
                # count of documents
                "total_count": [
                    {"$count": "count"}
                ]
            }
        },
        {
            # Deconstruct a total_count array to a single value
            "$unwind": "$total_count"
        },
        {
            "$project": {
                "items": 1,
                # get a count of products
                "count": "$total_count.count"
            }
        }
    ]

    product_list = await db.products.aggregate(pipeline=pipeline).to_list(length=None)

    products_count = product_list[0].get("count", 0)

    result = {
        # list of products
        "products": product_list[0].get("items", []),
        # Count of pages
        "page_count": ceil(products_count / page_size),
        # Count of products
        "items_count": products_count,
    }
    return result


async def get_product_details(product_id: PyObjectId):
    pipeline = [
        # Match product with the specified id
        {
            "$match": {
                "_id": product_id
            }
        },
        # Join product variations
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "parent_id",
                "pipeline": [
                    {
                        "$project": {
                            "extra_attrs": 0,
                            "parent_id": 0,
                            "category": 0,
                            "variation_theme": 0,
                            "for_sale": 0,
                            "same_images": 0,
                        }
                    }
                ],
                "as": "variations",
            }
        },
        {
            "$project": {
                "parent_id": 0,
            }
        },
        {
            "$addFields": {
                # get all attribute codes
                "attr_codes": {
                    "$map": {
                        "input": "$attrs",
                        "as": "attr",
                        "in": "$$attr.code"
                    }
                },
                # Include variations to the output only if the product is the parent.
                "variations": {
                    "$cond": {
                        "if": {"$eq": ["$parent", True]},
                        "then": "$variations",
                        "else": "$$REMOVE"
                    }
                },
            }
        }
    ]

    product = await db.products.aggregate(pipeline=pipeline).to_list(length=None)
    product = product[0]

    # get facets where code equals to one from product["attr_codes"] list
    facets = await db.facets.find({"code": {"$in": product.pop("attr_codes", [])}}).to_list(length=None)

    # get category where _id equals to product's category field.
    category = await db.categories.find_one({"_id": product.get("category")}, {"_id": 0, "name": 1, "groups": 1})

    variation_theme = None
    # if there is a variation theme and product is the parent, then query a variation theme with _id equals to
    # product's variation_theme field
    if product["variation_theme"] is not None and product["parent"]:
        variation_theme = await db.variation_themes.find_one({"_id": product["variation_theme"], },
                                                             {"_id": 0, "name": 1, "filters": 1})
        # get filters (list of objects which store attribute codes)
        filters = variation_theme.pop("filters", [])
        field_codes = []
        for attr_filter in filters:
            filter_field_codes = attr_filter.get("field_codes", [])
            # Add items from the filter's field_codes list to the field_codes list above
            field_codes.extend(filter_field_codes)

        variation_theme["field_codes"] = field_codes



    result = {
        "product": product,
        "facets": facets,
        "variation_theme": variation_theme,
        "category": category
    }

    return result



