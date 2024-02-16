from typing import List, Dict

from bson import ObjectId


def get_variations_lookup_pipeline() -> List[Dict]:
    pipeline = [
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

    return pipeline


def get_product_detail(product_id: ObjectId, variations_lookup_pipeline: List[Dict]) -> List[Dict]:
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
                "pipeline": variations_lookup_pipeline,  # execute pipeline for each joined variation
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
    return pipeline
