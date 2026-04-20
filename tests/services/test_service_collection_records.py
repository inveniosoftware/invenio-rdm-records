# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test collections service integration with RDM records."""

import uuid
from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity
from invenio_collections.api import Collection, CollectionTree

from invenio_rdm_records.proxies import current_community_collections_service


@pytest.fixture()
def collection_tree(db, community):
    """Create a collection tree for a community."""
    unique_id = str(uuid.uuid4())[:8]
    tree = CollectionTree.create(
        title="Test Tree",
        order=10,
        namespace_id=community.id,
        slug=f"test-tree-{unique_id}",
    )
    return tree


@pytest.fixture()
def collection_foo(db, collection_tree):
    """Create a collection matching 'foo' titles."""
    return Collection.create(
        title="Foo Collection",
        search_query="metadata.title:foo",
        slug="foo-collection",
        ctree=collection_tree,
    )


def test_preview_collection_records(
    db,
    collection_tree,
    collection_foo,
    community,
    record_community,
    minimal_record,
    search_clear,
):
    """Test preview with collection slug and additional query."""
    rec1 = deepcopy(minimal_record)
    rec1["metadata"]["title"] = "foo additional research"
    record_community.create_record(record_dict=rec1, community=community)

    rec2 = deepcopy(minimal_record)
    rec2["metadata"]["title"] = "foo only"
    record_community.create_record(record_dict=rec2, community=community)

    rec3 = deepcopy(minimal_record)
    rec3["metadata"]["title"] = "bar test"
    record_community.create_record(record_dict=rec3, community=community)

    result = current_community_collections_service.preview_collection_records(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=collection_tree.slug,
        slug=collection_foo.slug,
        data={"search_query": "metadata.title:additional"},
    )

    assert result is not None
    assert hasattr(result, "total")
    assert result.total == 1, f"Expected 1 record, got {result.total}"


def test_preview_collection_records_no_slug(
    db,
    collection_tree,
    community,
    record_community,
    minimal_record,
    search_clear,
):
    """Test preview without a collection slug (pure query)."""
    rec1 = deepcopy(minimal_record)
    rec1["metadata"]["title"] = "test research paper"
    record_community.create_record(record_dict=rec1, community=community)

    rec2 = deepcopy(minimal_record)
    rec2["metadata"]["title"] = "another test study"
    record_community.create_record(record_dict=rec2, community=community)

    rec3 = deepcopy(minimal_record)
    rec3["metadata"]["title"] = "random research"
    record_community.create_record(record_dict=rec3, community=community)

    result = current_community_collections_service.preview_collection_records(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=collection_tree.slug,
        slug=None,
        data={"search_query": "metadata.title:test"},
    )

    assert result is not None
    assert hasattr(result, "total")
    assert result.total == 2, f"Expected 2 records, got {result.total}"


def test_preview_collection_records_optional_query(
    db,
    collection_tree,
    collection_foo,
    community,
    record_community,
    minimal_record,
    search_clear,
):
    """Test preview with collection but no additional query."""
    rec1 = deepcopy(minimal_record)
    rec1["metadata"]["title"] = "foo paper one"
    record_community.create_record(record_dict=rec1, community=community)

    rec2 = deepcopy(minimal_record)
    rec2["metadata"]["title"] = "foo paper two"
    record_community.create_record(record_dict=rec2, community=community)

    rec3 = deepcopy(minimal_record)
    rec3["metadata"]["title"] = "bar paper"
    record_community.create_record(record_dict=rec3, community=community)

    result = current_community_collections_service.preview_collection_records(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=collection_tree.slug,
        slug=collection_foo.slug,
        data={},
    )

    assert result is not None
    assert hasattr(result, "total")
    assert result.total == 2, f"Expected 2 records, got {result.total}"


def test_preview_collection_records_invalid_query(
    db,
    collection_tree,
    collection_foo,
    community,
):
    """Test that an invalid search query raises a ValidationError."""
    from marshmallow import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        current_community_collections_service.preview_collection_records(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug=collection_tree.slug,
            slug=collection_foo.slug,
            data={"search_query": "title:[unclosed bracket"},
        )

    errors = exc_info.value.messages
    assert errors
    assert "Invalid search query" in str(errors)


def test_namespace_id_resolution_by_slug(db, community, community_owner, running_app):
    """Test that namespace_id can be resolved from community slug."""
    running_app.app.config["COMMUNITIES_COLLECTIONS_ENABLED"] = True
    community_slug = community._record.get("slug", community.id)
    tree = current_community_collections_service.create_tree(
        identity=community_owner.identity,
        namespace_id=community_slug,
        data={
            "slug": "test-slug-resolution",
            "title": "Test Slug Resolution",
            "order": 1,
        },
    )

    assert tree._tree.slug == "test-slug-resolution"
    assert str(tree._tree.namespace_id) == str(community.id)

    running_app.app.config["COMMUNITIES_COLLECTIONS_ENABLED"] = False
