from src.config.settings import ATLAS_SEARCH_INDEX_NAME_SEARCH_TERMS


def get_search_terms_list_pipeline(page: int, page_size: int, name: str):
    pipeline = []

    if name:
        pipeline.append({
            "$search": {
                "index": ATLAS_SEARCH_INDEX_NAME_SEARCH_TERMS,
                "autocomplete": {
                    "query": name,
                    "path": "name",
                },
            }
        })

    pipeline.extend([
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
    ])

    return pipeline
