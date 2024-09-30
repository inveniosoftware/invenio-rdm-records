# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test suite for the collections programmatic API."""

from invenio_rdm_records.collections.api import Collection, CollectionTree


def test_create(running_app, db, community, community_owner):
    """Test collection creation via API."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        community_id=community.id,
        slug="tree-1",
    )

    # Use ORM object (collection tree)
    collection = Collection.create(
        title="My Collection",
        query="*:*",
        slug="my-collection",
        ctree=tree,
    )

    read_c = Collection.resolve(collection.id)
    assert read_c.id == collection.id
    assert read_c.title == "My Collection"
    assert read_c.collection_tree.id == tree.id

    # Use collection tree id
    collection = Collection.create(
        title="My Collection 2",
        query="*:*",
        slug="my-collection-2",
        ctree=tree.id,
    )

    read_c = Collection.resolve(collection.id)
    assert read_c.id == collection.id
    assert collection.title == "My Collection 2"
    assert collection.collection_tree.id == tree.id


def test_as_dict(running_app, db):
    """Test collection as dict."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        slug="tree-1",
    )
    c1 = Collection.create(
        title="My Collection",
        query="*:*",
        slug="my-collection",
        ctree=tree,
    )

    c2 = Collection.create(
        title="My Collection 2",
        query="*:*",
        slug="my-collection-2",
        parent=c1,
    )

    c3 = Collection.create(title="3", query="*", slug="my-collection-3", parent=c2)
    res = c1.to_dict(max_depth=3)
    assert all(k in res for k in (c1.id, c2.id, c3.id))
    assert res[c1.id]["title"] == "My Collection"
    assert res[c1.id]["children"] == [c2.id]
    assert res[c2.id]["children"] == [c3.id]
    assert res[c3.id]["children"] == []

    res = c1.to_dict(max_depth=2)
    assert all(k in res for k in (c1.id, c2.id))
    assert res[c1.id]["title"] == "My Collection"
    assert res[c1.id]["children"] == [c2.id]
    assert res[c2.id]["children"] == []
    assert c3.id not in res


def test_query_build(running_app, db):
    """Test query building."""

    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        slug="tree-1",
    )
    c1 = Collection.create(
        title="My Collection",
        query="metadata.title:hello",
        slug="my-collection",
        ctree=tree,
    )
    c2 = Collection.create(
        title="My Collection 2",
        query="metadata.creators.name:john",
        slug="my-collection-2",
        parent=c1,
    )
    assert c2.query == "(metadata.title:hello) AND (metadata.creators.name:john)"


def test_children(running_app, db):
    """Test children property."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        slug="tree-1",
    )
    c1 = Collection.create(
        title="My Collection",
        query="*:*",
        slug="my-collection",
        ctree=tree,
    )
    c2 = Collection.create(
        title="My Collection 2",
        query="*:*",
        slug="my-collection-2",
        parent=c1,
    )
    c3 = Collection.create(
        title="My Collection 3",
        query="*:*",
        slug="my-collection-3",
        parent=c2,
    )
    assert c1.children == [c2]
    assert c2.children == [c3]
    assert c3.children == []
