def get_facet_list_pipeline(filters: dict, page: int, page_size: int):
    pipeline = [
        {
            "$match": {
                **filters
            }
        },
        {
            "$facet": {
                "result": [
                    {
                        "$project": {
                            "values": 0,
                            "categories": 0
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
