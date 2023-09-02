class CategoryTree:

    def __init__(self, categories: list[dict]) -> None:
        self.categories = categories

    def get_roots(self):
        return [c for c in self.categories if c["parent"] is None]

    def get_nodes(self, tree_id):
        # Filter the categories list by matching the tree_id
        nodes = [c for c in self.categories if c["tree_id"] == tree_id]
        return sorted(nodes, key=lambda c: c["level"])

    # A method that returns a list of children that have the same tree_id and
    # level higher than the category
    # passed as a parameter
    def get_children_list(self, category):
        # Get the tree_id and level of the category
        tree_id = category["tree_id"]
        level = category["level"]
        # Filter the categories list by matching the tree_id and comparing the level
        return list(filter(lambda c: c["tree_id"] == tree_id and c["level"] > level, self.categories))

    # A method that recursively populates the children field of a given category
    def _populate_children(self, category):
        # Find the categories that have the node id as their parent
        children = [c for c in self.categories if c["parent"] == category["_id"]]
        # For each child category, populate its children field by calling the method
        # recursively
        for child in children:
            child["children"] = self._populate_children(child)
        # Return the array of children
        return children

    # A method that returns a category tree with the given category as the root
    def get_tree(self, category_id):
        # Find the category that has the node id as its id
        root = next(c for c in self.categories if c["_id"] == category_id)
        # Populate its children field
        root["children"] = self._populate_children(root)
        # Return the root node with its children
        return root

    # A method that returns the whole tree of categories
    def get_whole_tree(self):
        # Get a list of root categories
        roots = self.get_roots()
        # For each root category, populate its children field
        for root in roots:
            root["children"] = self._populate_children(root)
        # Return the list of root categories with their children
        return roots
