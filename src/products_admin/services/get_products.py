from math import ceil

from fastapi import HTTPException

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
                                },
                                {
                                    "$sort": {"price": 1}
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

    # If there are no products, then
    # return empty list, page count 0, items count 0
    if not product_list:
        return {
            # list of products
            "products": [],
            # Count of pages
            "page_count": 1,
            # Count of products
            "items_count": 0,
        }

    # otherwise, return product list, product count, page count from query
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
    # Pipeline that executes on product variations join
    variations_lookup_pipeline = [
        {
            "$addFields": {
                # Get all field codes from variation theme
                "field_codes": {
                    "$reduce":
                        {
                            "input": "$variation_theme.options",
                            "initialValue": [],
                            "in": {
                                "$concatArrays": ["$$value", "$$this.field_codes"]
                            }
                        }

                },
            }
        },
        {
            "$addFields": {
                # Filter attributes by attribute code. Attribute code should in field_codes array
                "attrs": {
                    "$filter": {
                        "input": "$attrs",
                        "as": "attr",
                        "cond": {
                            "$in": ["$$attr.code", "$field_codes"]
                        }
                    }
                },
            }
        },
        {
            "$project": {
                "extra_attrs": 0,
                "parent_id": 0,
                "category": 0,
                "variation_theme": 0,
                "for_sale": 0,
                "same_images": 0,
                "is_filterable": 0,
                "field_codes": 0,
            }
        },
        {
            "$sort": {"price": 1}
        }
    ]

    # Main aggregation pipeline
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
                "pipeline": variations_lookup_pipeline,
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
                # Include variations to the output only if the product is the parent.
                "variations": {
                    "$cond": {
                        "if": {"$eq": ["$parent", True]},
                        "then": "$variations",
                        "else": "$$REMOVE"
                    }
                },
                # get all attribute codes
                "attr_codes": {
                    "$map": {
                        "input": "$attrs",
                        "as": "attr",
                        "in": "$$attr.code"
                    }
                },
            }
        }
    ]

    product = await db.products.aggregate(pipeline=pipeline).to_list(length=None)
    product = product[0]

    # if product not found, then raise HTTP 404 Not Found
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # get facets where code equals to one from product["attr_codes"] list
    # OR category is equal to product.category or equal to "*"
    facets = await db.facets.find(
        {"$or":[
            {"code": {"$in": product.pop("attr_codes", [])}},
            {"categories": {"$in": [product.get("category"), "*"]}}
        ]
         }
    ).to_list(length=None)

    # get category where _id equals to product's category field.
    category = await db.categories.find_one({"_id": product.get("category")}, {"_id": 0, "name": 1, "groups": 1})

    # get facet types
    facet_types = await db.facet_types.find({"value": {"$ne": "list"}}, {"_id": 0, }).to_list(length=None)


    if product.get("parent"):
        # get variation theme
        variation_theme = dict(product.get("variation_theme"))

        # initialize list where field_codes from variation theme is stored
        field_codes = []

        for option in variation_theme.pop("options", []):
            # get field_codes from each option in variation theme options
            field_codes.extend(option.get("field_codes", []))

        # Assign field_codes property to list of all field codes in options
        variation_theme["field_codes"] = field_codes
    else:
        variation_theme = None

    result = {
        "product": product,
        "facets": facets,
        "variation_theme": variation_theme,
        "category": category,
        "facet_types": facet_types,
    }

    return result
