# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service items."""

from invenio_records_resources.services.base.results import (
    ServiceItemResult,
    ServiceListResult,
)


class CollectionItem(ServiceItemResult):
    """Collection item."""

    def __init__(self, identity, collection, schema, links_tpl):
        """Instantiate a Collection object.

        Optionally pass a community to cache its information in the collection's instance.
        """
        self._identity = identity
        self._collection = collection
        self._schema = schema
        self._links_tpl = links_tpl

    def to_dict(self):
        """Serialize the collection to a dictionary and add links.

        It will output a dictionary with the following structure:

        .. code-block:: python

            {
                "root": 1,
                1: {
                    "id": 1,
                    "title": "Root",
                    "slug": "root",
                    "depth": 0,
                    "order": 1,
                    "query": "",
                    "num_records": 0,
                    "children": [2],
                    "links": {
                        "self_html": "..."
                        "search": "..."
                    }
                },
                2: {
                    "id": 2,
                    "title": "Subcollection",
                    "slug": "subcollection",
                    "depth": 1,
                    "order": 1,
                    "query": "",
                    "num_records": 0,
                    "children": [],
                    "links": {
                        "self_html": "..."
                        "search": "..."
                    }
                }
        """
        res = {
            "root": self._collection.id,
            self._collection.id: {
                **self._schema.dump(
                    self._collection, context={"identity": self._identity}
                ),
                "children": list(),
                "links": self._links_tpl.expand(self._identity, self._collection),
            },
        }

        for _c in self._collection.subcollections:
            if _c.id not in res:
                # Add the subcollection to the dictionary
                res[_c.id] = {
                    **self._schema.dump(_c, context={"identity": self._identity}),
                    "children": list(),
                    "links": self._links_tpl.expand(self._identity, _c),
                }
            # Find the parent ID from the collection's path (last valid ID in the path)
            path_parts = _c.split_path_to_ids()
            if path_parts:
                parent_id = path_parts[-1]
                # Add the collection as a child of its parent
                res[parent_id]["children"].append(_c.id)

        # Add breadcrumbs, sorted from root to leaf and taking into account the `order` field
        res[self._collection.id]["breadcrumbs"] = self.breadcrumbs

        return res

    @property
    def breadcrumbs(self):
        """Get the collection ancestors."""
        res = []
        for anc in self._collection.ancestors:
            _a = {
                "title": anc.title,
                "link": self._links_tpl.expand(self._identity, anc)["self_html"],
            }
            res.append(_a)
        res.append(
            {
                "title": self._collection.title,
                "link": self._links_tpl.expand(self._identity, self._collection)[
                    "self_html"
                ],
            }
        )
        return res

    @property
    def query(self):
        """Get the collection query."""
        return self._collection.query


class CollectionList(ServiceListResult):
    """Collection list item."""

    def __init__(self, identity, collections, schema, links_tpl, links_item_tpl):
        """Instantiate a Collection list item."""
        self._identity = identity
        self._collections = collections
        self._schema = schema
        self._links_tpl = links_tpl
        self._links_item_tpl = links_item_tpl

    def to_dict(self):
        """Serialize the collection list to a dictionary."""
        res = []
        for collection in self._collections:
            _r = CollectionItem(
                self._identity, collection, self._schema, self._links_item_tpl
            ).to_dict()
            res.append(_r)
        return res

    def __iter__(self):
        """Iterate over the collections."""
        return (
            CollectionItem(self._identity, x, self._schema, self._links_item_tpl)
            for x in self._collections
        )


class CollectionTreeItem:
    """Collection tree item."""

    def __init__(self, identity, tree, collection_link_tpl, collection_schema):
        """Instantiate a Collection tree object."""
        self._identity = identity
        self._tree = tree
        self._collection_link_tpl = collection_link_tpl
        self._collection_schema = collection_schema

    def to_dict(self):
        """Serialize the collection tree to a dictionary."""
        return {
            "title": self._tree.title,
            "slug": self._tree.slug,
            "community_id": str(self._tree.community_id),
            "order": self._tree.order,
            "id": self._tree.id,
            "collections": [
                CollectionItem(
                    self._identity,
                    c,
                    self._collection_schema,
                    self._collection_link_tpl,
                ).to_dict()
                for c in self._tree.collections
            ],
        }


class CollectionTreeList:
    """Collection tree list item."""

    def __init__(self, identity, trees, collection_schema, collection_link_tpl):
        """Instantiate a Collection tree list item."""
        self._identity = identity
        self._trees = trees
        self._collection_link_tpl = collection_link_tpl
        self._collection_schema = collection_schema

    def to_dict(self):
        """Serialize the collection tree list to a dictionary."""
        res = {}
        for tree in self._trees:
            # Only root collections
            res[tree.id] = CollectionTreeItem(
                self._identity,
                tree,
                self._collection_schema,
                self._collection_link_tpl,
            ).to_dict()
        return res

    def __iter__(self):
        """Iterate over the collection trees."""
        return iter(self._trees)
