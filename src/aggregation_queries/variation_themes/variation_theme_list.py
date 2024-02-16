def get_variation_theme_list_pipeline(page: int, page_size: int):
    pipeline = [
        {
            "$facet": {
                "result": [
                    {
                        "$project": {
                            "_id": 1,
                            "name": 1
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