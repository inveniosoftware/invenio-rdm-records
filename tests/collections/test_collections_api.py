# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test suite for the collections programmatic API."""

from invenio_search.engine import dsl

from invenio_rdm_records.collections.api import Collection, CollectionTree


def test_create(running_app, db, community, community_owner):
    """Test collection creation via API."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        community_id=community.id,
        slug="tree-1",
    )

    collection = Collection.create(
        title="My Collection",
        query="*:*",
        slug="my-collection",
        ctree=tree,
    )

    read_c = Collection.read(id_=collection.id)
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

    read_c = Collection.read(id_=collection.id)
    assert read_c.id == collection.id
    assert collection.title == "My Collection 2"
    assert collection.collection_tree.id == tree.id


def test_resolve(running_app, db, community):
    """Test collection resolution."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        community_id=community.id,
        slug="tree-1",
    )

    collection = Collection.create(
        title="My Collection",
        query="*:*",
        slug="my-collection",
        ctree=tree,
    )

    # Read by ID
    read_by_id = Collection.read(id_=collection.id)
    assert read_by_id.id == collection.id

    # Read by slug
    read_by_slug = Collection.read(slug="my-collection", ctree_id=tree.id)
    assert read_by_slug.id == read_by_id.id == collection.id


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
    assert c2.query == c1.query & dsl.Q("query_string", query=c2.search_query)


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
