def get_search_terms_list_pipeline(page: int, page_size: int):
    pipeline = [
        {
            "$facet": {
                "result": [
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
