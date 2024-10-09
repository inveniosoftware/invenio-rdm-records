# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service."""

import os

from flask import current_app, url_for
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.uow import ModelCommitOp, unit_of_work

from .api import Collection, CollectionTree
from .errors import LogoNotFoundError
from .results import CollectionItem, CollectionTreeList


class CollectionsService:
    """Collections service."""

    collection_cls = Collection

    @unit_of_work()
    def create(
        self, identity, community_id, tree_slug, slug, title, query, uow=None, **kwargs
    ):
        """Create a new collection."""
        current_communities.service.require_permission(
            identity, "update", community_id=community_id
        )
        ctree = CollectionTree.resolve(slug=tree_slug, community_id=community_id)
        collection = self.collection_cls.create(
            slug=slug, title=title, query=query, ctree=ctree, **kwargs
        )
        uow.register(ModelCommitOp(collection.model))
        return CollectionItem(collection)

    def read(
        self, identity, /, *, id_=None, slug=None, community_id=None, tree_slug=None
    ):
        """Get a collection by ID or slug.

        To resolve by slug, the collection tree ID and community ID must be provided.
        """
        if id_:
            collection = self.collection_cls.resolve(id_)
        elif slug and tree_slug and community_id:
            ctree = CollectionTree.resolve(slug=tree_slug, community_id=community_id)
            collection = self.collection_cls.resolve(slug=slug, ctree_id=ctree.id)
        else:
            raise ValueError(
                "ID or slug and tree_slug and community_id must be provided."
            )

        if collection.community:
            current_communities.service.require_permission(
                identity, "read", community_id=collection.community.id
            )

        return CollectionItem(collection)

    def list_trees(self, identity, community_id, max_depth=2):
        """Get the trees of a community."""
        current_communities.service.require_permission(
            identity, "read", community_id=community_id
        )
        if not community_id:
            raise ValueError("Community ID must be provided.")
        res = CollectionTree.get_community_trees(community_id)
        return CollectionTreeList(res, max_depth=max_depth)

    @unit_of_work()
    def add(self, identity, collection, slug, title, query, uow=None, **kwargs):
        """Add a subcollection to a collection."""
        current_communities.service.require_permission(
            identity, "update", community_id=collection.community.id
        )
        new_collection = self.collection_cls.create(
            parent=collection, slug=slug, title=title, query=query, **kwargs
        )
        uow.register(ModelCommitOp(new_collection.model))
        return CollectionItem(new_collection)

    def read_logo(self, identity, slug):
        """Read a collection logo.

        TODO: implement logos as files in the database. For now, we just check if the file exists as a static file.
        """
        logo_path = f"images/collections/{slug}.jpg"
        _exists = os.path.exists(os.path.join(current_app.static_folder, logo_path))
        if _exists:
            return url_for("static", filename=logo_path)
        raise LogoNotFoundError()
