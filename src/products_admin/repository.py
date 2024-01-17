from typing import Union, List

from bson import ObjectId
from pymongo.operations import UpdateOne

from src.database import db
from src.repositories.product_repository_base import ProductRepositoryBase


class ProductAdminRepository(ProductRepositoryBase):
    async def update_image_links(self, product_ids: Union[List[ObjectId], ObjectId],
                                 images: Union[List[dict], dict],
                                 same_images: bool = False):
        """
        Updates image links in products.
        :param product_ids: List of ObjectID or ObjectID. Products where image links will be updated.
        :param images: List of dicts or dict. Image links that will be inserted into the products.
        :param same_images: defines whether function should upload the same images to the products
        """
        # check if the input is a single product id or a list of product ids
        if isinstance(product_ids, list):
            # check if the same_images parameter is True
            if same_images:
                # use the update_many method with the $in operator to update the same images for the products in
                # the product_ids list
                await self.update_many_products(
                    {"_id": {"$in": product_ids}},
                    {"$set": {"images": images}}
                )
            else:
                # List of operations for bulkWrite
                operations = []
                # loop through the product ids and images
                for product_id, image in zip(product_ids, images):
                    # add the update_one method to the list of operations
                    operations.append(UpdateOne(
                        {"_id": product_id},
                        {"$set": {"images": image}}
                    ))
                await self.update_many_products_bulk(operations, ordered=False)
        else:
            # use the update_one method to update the image links for the single product
            await self.update_one_product(
                {"_id": product_ids},
                {"$set": {"images": images}}
            )

    async def get_product_details(self, product_id: ObjectId) -> dict:
        """
        Returns product details and its variations if they are present.
        """
        # Pipeline that executes on product variations join
        variations_lookup_pipeline = [
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

        # Main aggregation pipeline
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

        product = await db.products.aggregate(pipeline=pipeline).to_list(length=None)
        return product[0] if product else {}

    async def get_products_with_variations(self, page: int, page_size: int) -> dict:
        """
        :param page: page number. Suppose for each page you have 5 items. If the page number is 1,
        then db will return only first 5 items. If the page number is 2, then the database will skip the first 5 items,
        and return 5 items after the previous 5 items.
        :param page_size: count of items per page.
        :return: Products, their variations and count of products.
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
                                "pipeline": [
                                    {
                                        "$project": {
                                            **product_projection,
                                            # Add a tax field, for each joined product
                                            "tax": {"$round": [{"$multiply": ["$price", "$tax_rate"]}, 2]}
                                        }
                                    },
                                    {
                                        "$sort": {"price": 1}
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
        return product_list[0] if product_list else {}
