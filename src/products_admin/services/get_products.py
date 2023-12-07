from math import ceil
from src.database import db

async def get_product_list(page: int, page_size: int):
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
                            "as": "variations"
                        }
                    },
                    {
                        "$project": {
                            **product_projection,
                            "variations": {
                                "_id": 1,
                                **product_projection,
                            }
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