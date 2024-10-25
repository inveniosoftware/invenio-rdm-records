# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test suite for the collections service."""

import dictdiffer
import pytest

from invenio_rdm_records.collections.api import Collection, CollectionTree
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
        tree = CollectionTree.create(
            title="Tree 1",
            order=10,
            community_id=community.id,
            slug="tree-1",
        )
        c1 = Collection.create(
            title="Collection 1",
            query="metadata.title:foo",
            slug="collection-1",
            ctree=tree,
        )
        c2 = Collection.create(
            title="Collection 2",
            query="metadata.title:bar",
            slug="collection-2",
            ctree=tree,
            parent=c1,
        )
        return [c1, c2]

    return _inner


def test_collections_read(
    running_app, db, add_collections, collections_service, community, community_owner
):
    """Test collections service."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]

    # Read by id
    res = collections_service.read(identity=community_owner.identity, id_=c0.id)
    assert res._collection.id == c0.id

    # Read by slug
    res = collections_service.read(
        identity=community_owner.identity,
        community_id=community.id,
        tree_slug=c0.collection_tree.slug,
        slug=c0.slug,
    )
    assert res._collection.id == c0.id


def test_collections_create(
    running_app, db, collections_service, community, community_owner
):
    """Test collection creation via service."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        community_id=community.id,
        slug="tree-1",
    )
    collection = collections_service.create(
        community_owner.identity,
        community.id,
        tree_slug="tree-1",
        slug="my-collection",
        title="My Collection",
        query="*:*",
    )

    # Get the API object, just for the sake of testing
    collection = collection._collection

    assert collection.title == "My Collection"
    assert collection.collection_tree.id == tree.id

    read_collection = collections_service.read(
        identity=community_owner.identity, id_=collection.id
    )
    assert read_collection._collection.id == collection.id
    assert read_collection._collection.title == "My Collection"


def test_collections_add(
    running_app, db, collections_service, add_collections, community_owner
):
    """Test adding a collection to another via service."""
    collections = add_collections()
    c1 = collections[0]
    c2 = collections[1]

    c3 = collections_service.add(
        community_owner.identity,
        collection=c2,
        slug="collection-3",
        title="Collection 3",
        query="metadata.title:baz",
    )

    # Get the API object, just for the sake of testing
    c3 = c3._collection

    # Read the collection
    res = collections_service.read(identity=community_owner.identity, id_=c3.id)
    assert res._collection.id == c3.id
    assert res._collection.title == "Collection 3"

    # Read the parent collection
    res = collections_service.read(identity=community_owner.identity, id_=c2.id)
    assert res.to_dict()[c2.id]["children"] == [c3.id]


def test_collections_results(
    running_app, db, add_collections, collections_service, community_owner
):
    """Test collection results.

    The goal is to test the format returned by the service, based on the required depth.
    """
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]
    c3 = collections_service.add(
        community_owner.identity,
        c1,
        slug="collection-3",
        title="Collection 3",
        query="metadata.title:baz",
    )
    # Read the collection tree up to depth 2
    res = collections_service.read(
        identity=community_owner.identity, id_=c0.id, depth=2
    )
    r_dict = res.to_dict()

    expected = {
        "root": c0.id,
        c0.id: {
            "breadcrumbs": [
                {
                    "link": "/communities/blr/collections/tree-1/collection-1",
                    "title": "Collection 1",
                }
            ],
            "children": [c1.id],
            "depth": 0,
            "id": c0.id,
            "links": {
                "search": "/api/communities/blr/records",
                "self_html": "/communities/blr/collections/tree-1/collection-1",
                "search": f"/api/collections/{c0.id}/records",
            },
            "num_records": 0,
            "order": c0.order,
            "slug": "collection-1",
            "title": "Collection 1",
        },
        c1.id: {
            "children": [],
            "depth": 1,
            "id": c1.id,
            "links": {
                "search": "/api/communities/blr/records",
                "self_html": "/communities/blr/collections/tree-1/collection-2",
                "search": f"/api/collections/{c1.id}/records",
            },
            "num_records": 0,
            "order": c1.order,
            "slug": "collection-2",
            "title": "Collection 2",
        },
    }
    assert not list(dictdiffer.diff(expected, r_dict))

    # Read the collection tree up to depth 3
    res = collections_service.read(
        identity=community_owner.identity, id_=c0.id, depth=3
    )
    r_dict = res.to_dict()

    # Get the API object, just for the sake of testing
    c3 = c3._collection
    expected = {
        "root": c0.id,
        c0.id: {
            "breadcrumbs": [
                {
                    "link": "/communities/blr/collections/tree-1/collection-1",
                    "title": "Collection 1",
                }
            ],
            "children": [c1.id],
            "depth": 0,
            "id": c0.id,
            "links": {
                "search": "/api/communities/blr/records",
                "self_html": "/communities/blr/collections/tree-1/collection-1",
                "search": f"/api/collections/{c0.id}/records",
            },
            "num_records": 0,
            "order": c0.order,
            "slug": "collection-1",
            "title": "Collection 1",
        },
        c1.id: {
            "children": [c3.id],
            "depth": 1,
            "id": c1.id,
            "links": {
                "search": "/api/communities/blr/records",
                "self_html": "/communities/blr/collections/tree-1/collection-2",
                "search": f"/api/collections/{c1.id}/records",
            },
            "num_records": 0,
            "order": c1.order,
            "slug": "collection-2",
            "title": "Collection 2",
        },
        c3.id: {
            "children": [],
            "depth": 2,
            "id": c3.id,
            "links": {
                "search": "/api/communities/blr/records",
                "self_html": "/communities/blr/collections/tree-1/collection-3",
                "search": f"/api/collections/{c3.id}/records",
            },
            "num_records": 0,
            "order": c3.order,
            "slug": "collection-3",
            "title": "Collection 3",
        },
    }

    assert not list(dictdiffer.diff(expected, r_dict))


def test_update(running_app, db, add_collections, collections_service, community_owner):
    """Test updating a collection."""
    collections = add_collections()
    c0 = collections[0]

    # Update by ID
    collections_service.update(
        community_owner.identity,
        c0.id,
        data={"slug": "New slug"},
    )

    res = collections_service.read(
        identity=community_owner.identity,
        id_=c0.id,
    )

    assert res.to_dict()[c0.id]["slug"] == "New slug"

    # Update by object
    collections_service.update(
        community_owner.identity,
        c0,
        data={"slug": "New slug 2"},
    )

    res = collections_service.read(
        identity=community_owner.identity,
        id_=c0.id,
    )
    assert res.to_dict()[c0.id]["slug"] == "New slug 2"


def test_read_many(
    running_app, db, add_collections, collections_service, community_owner
):
    """Test reading multiple collections."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]

    # Read two collections
    res = collections_service.read_many(
        community_owner.identity,
        ids_=[c0.id, c1.id],
        depth=0,
    )

    res = res.to_dict()
    assert len(res) == 2
    assert res[0]["root"] == c0.id
    assert res[1]["root"] == c1.id


def test_read_all(
    running_app, db, add_collections, collections_service, community_owner
):
    """Test reading all collections."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]

    # Read all collections
    res = collections_service.read_all(community_owner.identity, depth=0)

    res = res.to_dict()
    assert len(res) == 2
    assert res[0]["root"] == c0.id
    assert res[1]["root"] == c1.id


def test_read_invalid(running_app, db, collections_service, community_owner):
    """Test reading a non-existing collection."""
    with pytest.raises(ValueError):
        collections_service.read(
            identity=community_owner.identity,
        )
