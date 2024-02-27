def get_deal_list_pipeline(filters: dict, page: int, page_size: int):
    pipeline = [
        {
            "$match": filters,
        },
        {
            "$facet": {
                "result": [
                    {
                        "$lookup": {
                            "from": "deals",
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
                            "name": 1,
                            "is_parent": 1,
                            "parent_name": 1,
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
            },
        },
        {
            "$unwind": "$total_count",
        },
    ]

    return pipeline
