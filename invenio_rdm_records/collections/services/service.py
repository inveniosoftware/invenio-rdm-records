# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service."""

import os

from flask import current_app, url_for
from invenio_records_resources.services import ServiceSchemaWrapper
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import ModelCommitOp, unit_of_work

from invenio_rdm_records.proxies import (
    current_community_records_service,
    current_rdm_records_service,
)

from ..api import Collection, CollectionTree
from ..errors import LogoNotFoundError
from .links import CollectionLinkstemplate
from .results import CollectionItem, CollectionList, CollectionTreeList


class CollectionsService(Service):
    """Collections service."""

    def __init__(self, config):
        """Instantiate the service with the given config."""
        self.config = config

    collection_cls = Collection

    @property
    def collection_schema(self):
        """Get the collection schema."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def links_item_tpl(self):
        """Get the item links template."""
        return CollectionLinkstemplate(
            links=self.config.links_item,
            context={
                "permission_policy_cls": self.config.permission_policy_cls,
            },
        )

    @unit_of_work()
    def create(
        self, identity, community_id, tree_slug, slug, title, query, uow=None, **kwargs
    ):
        """Create a new collection.

        The created collection will be added to the collection tree as a root collection (no parent).
        If a parent is needed, use the ``add`` method.
        """
        self.require_permission(identity, "update", community_id=community_id)
        ctree = CollectionTree.resolve(slug=tree_slug, community_id=community_id)
        collection = self.collection_cls.create(
            slug=slug, title=title, query=query, ctree=ctree, **kwargs
        )
        uow.register(ModelCommitOp(collection.model))
        return CollectionItem(
            identity, collection, self.collection_schema, self.links_item_tpl
        )

    def read(
        self,
        identity=None,
        *,
        id_=None,
        slug=None,
        community_id=None,
        tree_slug=None,
        depth=2,
        **kwargs,
    ):
        """Get a collection by ID or slug.

        To resolve by slug, the collection tree ID and community ID must be provided.
        """
        if id_:
            collection = self.collection_cls.read(id_=id_, depth=depth)
        elif slug and tree_slug and community_id:
            ctree = CollectionTree.resolve(slug=tree_slug, community_id=community_id)
            collection = self.collection_cls.read(
                slug=slug, ctree_id=ctree.id, depth=depth
            )
        else:
            raise ValueError(
                "ID or slug and tree_slug and community_id must be provided."
            )

        if collection.community:
            self.require_permission(
                identity, "read", community_id=collection.community.id
            )

        return CollectionItem(
            identity,
            collection,
            self.collection_schema,
            self.links_item_tpl,
        )

    def list_trees(self, identity, community_id, **kwargs):
        """Get the trees of a community."""
        self.require_permission(identity, "read", community_id=community_id)
        if not community_id:
            raise ValueError("Community ID must be provided.")
        res = CollectionTree.get_community_trees(community_id, **kwargs)
        return CollectionTreeList(
            identity, res, self.links_item_tpl, self.collection_schema
        )

    @unit_of_work()
    def add(self, identity, collection, slug, title, query, uow=None, **kwargs):
        """Add a subcollection to a collection."""
        self.require_permission(
            identity, "update", community_id=collection.community.id
        )
        new_collection = self.collection_cls.create(
            parent=collection, slug=slug, title=title, query=query, **kwargs
        )
        uow.register(ModelCommitOp(new_collection.model))
        return CollectionItem(
            identity, new_collection, self.collection_schema, self.links_item_tpl
        )

    @unit_of_work()
    def update(self, identity, collection_or_id, data=None, uow=None):
        """Update a collection."""
        if isinstance(collection_or_id, int):
            collection = self.collection_cls.read(id_=collection_or_id)
        else:
            collection = collection_or_id
        self.require_permission(
            identity, "update", community_id=collection.community.id
        )

        data = data or {}

        valid_data, errors = self.collection_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        res = collection.update(**valid_data)

        uow.register(ModelCommitOp(res.model))

        return CollectionItem(
            identity, collection, self.collection_schema, self.links_item_tpl
        )

    def read_logo(self, identity, slug):
        """Read a collection logo.

        TODO: implement logos as files in the database. For now, we just check if the file exists as a static file.
        """
        logo_path = f"images/collections/{slug}.jpg"
        _exists = os.path.exists(os.path.join(current_app.static_folder, logo_path))
        if _exists:
            return url_for("static", filename=logo_path)
        raise LogoNotFoundError()

    def read_many(self, identity, ids_, depth=2):
        """Get many collections."""
        self.require_permission(identity, "read")

        if ids_ is None:
            raise ValueError("IDs must be provided.")

        if ids_ == []:
            raise ValueError("Use read_all to get all collections.")

        res = self.collection_cls.read_many(ids_, depth=depth)
        return CollectionList(
            identity, res, self.collection_schema, None, self.links_item_tpl
        )

    def read_all(self, identity, depth=2):
        """Get all collections."""
        self.require_permission(identity, "read")
        res = self.collection_cls.read_all(depth=depth)
        return CollectionList(
            identity, res, self.collection_schema, None, self.links_item_tpl
        )

    def search_collection_records(self, identity, collection_or_id, params=None):
        """Search records in a collection."""
        params = params or {}

        if isinstance(collection_or_id, int):
            collection = self.collection_cls.read(id_=collection_or_id)
        else:
            collection = collection_or_id

        if collection.community:
            res = current_community_records_service.search(
                identity,
                community_id=collection.community.id,
                extra_filter=collection.query,
                params=params,
            )
        else:
            raise NotImplementedError(
                "Search for collections without community not supported."
            )
        return res
