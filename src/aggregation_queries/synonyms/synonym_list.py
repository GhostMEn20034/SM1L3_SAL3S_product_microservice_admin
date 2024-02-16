def get_synonym_list_pipeline(page: int, page_size: int, filters: dict):
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