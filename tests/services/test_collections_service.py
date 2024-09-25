# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
""" TODO """

import pytest

from invenio_rdm_records.collections.api import Collection
from invenio_rdm_records.collections.models import CollectionTree
from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def collections_service():
    """Get collections service fixture."""
    return current_rdm_records.collections_service


@pytest.fixture(autouse=True)
def add_collections(running_app, db, community):
    """Create collections on demand."""

    def _inner():
        """Add collections to the app."""
        tree = CollectionTree(
            title="Tree 1",
            order=10,
            community_id=community.id,
        )
        db.session.add(tree)
        db.session.flush()
        db.session.refresh(tree)
        c1 = Collection.create(
            title="Collection 1", query="*:*", slug="collection-1", ctree=tree
        )
        db.session.add(c1.model)
        db.session.flush()
        db.session.refresh(tree)
        c2 = Collection.create(
            title="Collection 2",
            query="*:*",
            slug="collection-2",
            ctree=tree,
            parent=c1,
        )
        db.session.add(c2.model)
        db.session.commit()
        return [c1, c2]

    return _inner


def test_collections_service_read(
    running_app, db, add_collections, collections_service, community_owner
):
    """Test collections service."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]
    res = collections_service.read(community_owner, c0.id)
    assert res._collection.id == c0.id


def test_collections_service_create(
    running_app, db, collections_service, community_owner
):
    """Test collections service create."""
    collections_service.create(
        community_owner, 1, title="My Collection", query="*:*", slug="my-collection"
    )
