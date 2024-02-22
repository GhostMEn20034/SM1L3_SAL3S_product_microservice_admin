def get_product_list_pipeline(page: int, page_size: int, product_projection: dict):
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
                                    "$sort": {"created_at": 1, "price": 1}
                                }
                            ],
                            "as": "variations"
                        }
                    },
                    {
                        "$project": {
                            # Compute tax in amount money (Product price * tax rate)
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
                    {
                        "$sort": {"created_at": 1}
                    }
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

    return pipeline


def get_search_products_pipeline_stage(name: str, atlas_search_index_name: str):
    pipeline_stage = {
        "$search": {
            "index": atlas_search_index_name,
            "autocomplete": {
                "path": "name",
                "query": name.strip(),
            },
        }
    }

    return pipeline_stage


def get_search_products_main_pipeline(filters: dict, product_pipeline: list):
    pipeline = [
        {"$match": filters},
        {"$facet": {
            "items": product_pipeline,
            "total_count": [
                {"$count": "count"},
            ]
        }},
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

    return pipeline
