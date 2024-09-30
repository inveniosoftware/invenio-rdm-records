# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service items."""


class CollectionItem:
    """Collection item."""

    def __init__(self, collection):
        """Instantiate a Collection object.

        Optionally pass a community to cache its information in the collection's instance.
        """
        self._collection = collection

    def to_dict(self, max_depth=2, include_breadcrumbs=False):
        """Serialize the collection to a dictionary and add links."""
        res = {**self._collection.to_dict(max_depth=max_depth)}

        # Add links for all the collections
        tree = self._collection.collection_tree
        community = self._collection.community
        for id_, coll in res.items():
            if id_ == "root":
                continue
            res[id_]["links"] = {
                "search": CollectionItem.search_link(community.slug),
                "self_html": CollectionItem.html_link(
                    community.slug, tree.slug, coll["slug"]
                ),
            }

        # Add breadcrumbs
        if include_breadcrumbs:
            res[self._collection.id]["breadcrumbs"] = self.breadcrumbs

        return res

    @classmethod
    def search_link(cls, community_slug):
        """Get the search link."""
        if community_slug:
            return f"/api/communities/{community_slug}/records"
        return "/api/records"

    @classmethod
    def html_link(cls, community_slug, tree_slug, collection_slug):
        """Get the HTML link."""
        if community_slug:
            return f"/communities/{community_slug}/collections/{tree_slug}/{collection_slug}"
        return f"/collections/{tree_slug}/{collection_slug}"

    @property
    def title(self):
        """Get the collection title."""
        return self._collection.title

    @property
    def query(self):
        """Get the collection query."""
        return self._collection.query

    @property
    def collection_tree(self):
        """Get the collection tree."""
        return self._collection.collection_tree

    @property
    def children(self):
        """Get the collection children."""
        return self._collection.children

    @property
    def community(self):
        """Get the collection community."""
        return self._collection.community

    @property
    def breadcrumbs(self):
        """Get the collection ancestors."""
        res = []
        community_slug = self.community.slug
        tree_slug = self.collection_tree.slug
        for anc in self._collection.ancestors:
            _a = {
                "title": anc.title,
                "link": CollectionItem.html_link(community_slug, tree_slug, anc.slug),
            }
            res.append(_a)
        res.append(
            {
                "title": self.title,
                "link": CollectionItem.html_link(
                    community_slug, tree_slug, self._collection.slug
                ),
            }
        )
        return res


class CollectionList:
    """Collection list item."""

    def __init__(self, collections):
        """Instantiate a Collection list item."""
        self._collections = collections

    def to_dict(self, max_depth=2):
        """Serialize the collection list to a dictionary."""
        res = []
        for collection in self._collections:
            _r = collection.to_dict(max_depth=2)
            _r["links"] = CollectionItem(collection).links
            res.append(_r)
        return res

    def __iter__(self):
        """Iterate over the collections."""
        return iter(self._collections)


class CollectionTreeItem:
    """Collection tree item."""

    def __init__(self, tree, max_depth=2):
        """Instantiate a Collection tree object."""
        self._tree = tree
        self._max_depth = max_depth

    def to_dict(self):
        """Serialize the collection tree to a dictionary."""
        return self._tree.to_dict(max_depth=self._max_depth)


class CollectionTreeList:
    """Collection tree list item."""

    def __init__(self, trees, max_depth=1):
        """Instantiate a Collection tree list item."""
        self._trees = trees
        self._max_depth = max_depth

    def to_dict(self):
        """Serialize the collection tree list to a dictionary."""
        res = {}
        for tree in self._trees:
            # Only root collections
            res[tree.id] = CollectionTreeItem(tree, self._max_depth).to_dict()
        return res

    def __iter__(self):
        """Iterate over the collection trees."""
        return iter(self._trees)
