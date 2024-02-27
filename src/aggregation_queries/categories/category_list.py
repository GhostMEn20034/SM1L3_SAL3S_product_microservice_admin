def get_category_list_pipeline(page: int, page_size: int):
    pipeline = [
        {
            "$facet": {
                "result": [
                    {
                        "$lookup": {
                            "from": "categories",
                            "localField": "parent_id",
                            "foreignField": "_id",
                            "as": "parent"
                        }
                    },
                    {
                        "$unwind": {"path": "$parent", "preserveNullAndEmptyArrays": True}
                    },
                    {
                        "$addFields": {
                            "parent_name": {
                                "$ifNull": ["$parent.name", "No parent"]
                            }
                        }
                    },
                    {
                        "$project": {
                            "parent": 0,
                        }
                    },
                    {
                        "$skip": (page - 1) * page_size
                    },
                    {
                        "$limit": page_size
                    }
                ],
                "total_count": [
                    {"$count": "total"}
                ]
            }
        },
        {
            "$unwind": "$total_count",
        },
    ]

    return pipeline
