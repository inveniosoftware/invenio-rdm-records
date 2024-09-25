# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service."""

from invenio_communities.proxies import current_communities

from .api import Collection, CollectionTree


class CollectionItem:
    """Collection item."""

    def __init__(self, collection: Collection):
        """Instantiate a Collection object.

        Optionally pass a community to cache its information in the collection's instance.
        """
        self._collection = collection

    def to_dict(self):
        """Serialize the collection to a dictionary and add links."""
        res = {**self._collection.to_dict()}
        res[self._collection.id]["links"] = self.links

        return res

    @property
    def links(self):
        """Return the links of the collection."""
        self_html = None
        search = None
        tree_slug = self._collection.collection_tree.slug
        if self._collection.community:
            self_html = f"/communities/{self._collection.community.slug}/{tree_slug}/{self._collection.slug}"
            search = f"/api/communities/{self._collection.community.slug}/records"
        else:
            self_html = f"/collections/{tree_slug}/{self._collection.slug}"
            search = "/api/records"
        return {
            "search": search,
            "self_html": self_html,
        }

    def __getattr__(self, name):
        """Delegate attribute access to the collection."""
        return getattr(self._collection, name)


class CollectionsService:
    """Collections service."""

    collection_cls = Collection

    def create(self, identity, community_id, tree_slug, slug, title, query, **kwargs):
        """Create a new collection."""
        current_communities.service.require_permission(
            identity, "update", community_id=community_id
        )
        ctree = CollectionTree.get_by_slug(tree_slug, community_id)
        if not ctree:
            raise ValueError(f"Collection tree {tree_slug} not found.")
        collection = self.collection_cls.create(
            slug=slug, title=title, query=query, ctree=ctree, **kwargs
        )
        return CollectionItem(collection)

    def read(self, identity, id_):
        """Get a collection by ID or slug."""
        collection = self.collection_cls.resolve(id_)
        if not collection:
            raise ValueError(f"Collection {id_} not found.")
        if collection.community:
            current_communities.service.require_permission(
                identity, "read", community_id=collection.community.id
            )

        return CollectionItem(collection)

    def read_slug(self, identity, community_id, tree_slug, slug):
        """Get a collection by slug."""
        current_communities.service.require_permission(
            identity, "read", community_id=community_id
        )

        ctree = CollectionTree.get_by_slug(tree_slug, community_id)
        if not ctree:
            raise ValueError(f"Collection tree {tree_slug} not found.")

        collection = self.collection_cls.resolve(slug, ctree.id, use_slug=True)
        if not collection:
            raise ValueError(f"Collection {slug} not found.")

        return CollectionItem(collection)

    def add(self, identity, collection, slug, title, query, **kwargs):
        """Add a subcollection to a collection."""
        current_communities.service.require_permission(
            identity, "update", community_id=collection.community.id
        )
        collection = self.collection_cls.create(
            parent=collection, slug=slug, title=title, query=query, **kwargs
        )
        return CollectionItem(collection)
