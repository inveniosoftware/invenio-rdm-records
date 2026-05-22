# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Test celery tasks of collections."""

from copy import deepcopy

from invenio_collections.api import Collection, CollectionTree

from invenio_rdm_records.collections.tasks import update_collections_size


def test_update_collections_size(app, db, record_factory, minimal_record, community):
    """Test update_collections_size task."""
    tree = CollectionTree.create(
        title="Tree 1",
        order=10,
        namespace_id=community.id,
        slug="tree-1",
    )

    collection = Collection.create(
        title="My Collection",
        search_query="metadata.title:foo",
        slug="my-collection",
        ctree=tree,
    )
    update_collections_size()

    # Check that the collections have been updated
    collection = Collection.read(id_=collection.id)
    assert collection.num_records == 0

    # Add a record that matches the collection
    rec = deepcopy(minimal_record)
    rec["metadata"]["title"] = "foo"
    record_factory.create_record(record_dict=rec, community=community)

    update_collections_size()

    collection = Collection.read(id_=collection.id)
    assert collection.num_records == 1
