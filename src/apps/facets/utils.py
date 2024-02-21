class FacetFiltersHandler:
    def __init__(self, facet_filters):
        self.facet_filters = facet_filters

    def generate_filters(self):
        categories = self.facet_filters.get("categories")
        types = self.facet_filters.get("type")
        optional = self.facet_filters.get("optional")
        show_in_filters = self.facet_filters.get("show_in_filter")

        filters = {
            key: value for key, value in [
                ("categories", {"$in": categories} if categories else None),
                ("type", {"$in": types} if types else None),
                ("optional", optional),
                ("show_in_filters", show_in_filters)
            ] if value is not None
        }

        return filters
