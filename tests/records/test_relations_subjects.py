# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
# Copyright (C) 2021 Northwestern University
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record relationships."""

from collections import namedtuple

import pytest
from invenio_access.permissions import system_identity
from invenio_records.systemfields.relations import InvalidRelationValue
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


@pytest.fixture(scope="module")
def subject_type(app):
    """Subject vocabulary type."""
    return vocabulary_service.create_type(system_identity, "subjects", "sub")


@pytest.fixture(scope="module")
def subject_item(app, subject_type):
    """Subject vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "A-D000007",
        "props": {
            "subject_label": "MeSH"
        },
        "tags": ["mesh"],
        "title": {
            "en": "Abdominal Injuries"
        },
        "type": "subjects"
    })

    Vocabulary.index.refresh()

    return vocab


RunningApp = namedtuple("RunningApp", [
    "app", "location", "resource_type_item", "subject_item"
])


@pytest.fixture
def running_app_w_subject(running_app, subject_item):
    return RunningApp(
        running_app.app,
        running_app.location,
        running_app.resource_type_item,
        subject_item
    )


#
# Tests
#
def test_subjects_field(running_app, minimal_record):
    """Subjects should be defined as a relation."""
    assert 'subjects' in RDMDraft.relations
    assert 'subjects' in RDMRecord.relations
    assert RDMDraft.relations.subjects


def test_subjects_validation(running_app_w_subject, minimal_record):
    """Tests data content validation."""
    # Valid id
    minimal_record["metadata"]["subjects"] = [{"id": "A-D000007"}]

    draft = RDMDraft.create(minimal_record)
    draft.commit()

    assert draft["metadata"]["subjects"] == [{"id": "A-D000007"}]

    # Invalid id
    minimal_record["metadata"]["subjects"] = [{"id": "invalid"}]

    pytest.raises(InvalidRelationValue, RDMDraft.create(minimal_record).commit)


def test_subjects_indexing(running_app_w_subject, minimal_record):
    """Test dereferencing characteristics/features really."""
    minimal_record["metadata"]["subjects"] = [{"id": "A-D000007"}]
    draft = RDMDraft.create(minimal_record).commit()

    # Dumping should return dereferenced representation
    dump = draft.dumps()
    assert dump["metadata"]["subjects"] == [{
        "id": "A-D000007",
        "title": {"en": "Abdominal Injuries"},
        "@v": f"{running_app_w_subject.subject_item._record.id}::1"
    }]
    # NOTE/WARNING: draft.dumps() modifies the draft too
    assert draft["metadata"]["subjects"] == [{
        "id": "A-D000007",
        "title": {"en": "Abdominal Injuries"},
        "@v": f"{running_app_w_subject.subject_item._record.id}::1"
    }]

    # Loading draft again should produce an identical record.
    loaded_draft = RDMDraft.loads(dump)
    assert dict(draft) == dict(loaded_draft)

    # Calling commit() should clear the dereferenced relation.
    draft.commit()
    assert draft["metadata"]["subjects"] == [{"id": "A-D000007"}]

    # subjects should be reachable through relations
    subject = next(draft.relations.subjects())
    assert "A-D000007" == subject["id"]
