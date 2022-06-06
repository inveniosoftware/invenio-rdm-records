# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
# Copyright (C) 2021 Northwestern University
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record relationships."""

import pytest
from invenio_records.systemfields.relations import InvalidRelationValue

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


#
# Tests
#
def test_subjects_field(running_app, minimal_record):
    """Subjects should be defined as a relation."""
    assert "subjects" in RDMDraft.relations
    assert "subjects" in RDMRecord.relations
    assert RDMDraft.relations.subjects


def test_subjects_validation(running_app, minimal_record):
    """Tests data content validation."""
    # Valid id
    minimal_record["metadata"]["subjects"] = [
        {"id": "http://id.nlm.nih.gov/mesh/A-D000007"}
    ]

    draft = RDMDraft.create(minimal_record)
    draft.commit()

    assert draft["metadata"]["subjects"] == [
        {"id": "http://id.nlm.nih.gov/mesh/A-D000007"}
    ]

    # Invalid id
    minimal_record["metadata"]["subjects"] = [{"id": "invalid"}]

    pytest.raises(InvalidRelationValue, RDMDraft.create(minimal_record).commit)


def test_subjects_indexing(running_app, minimal_record):
    """Test dereferencing characteristics/features really."""
    minimal_record["metadata"]["subjects"] = [
        {"id": "http://id.nlm.nih.gov/mesh/A-D000007"}
    ]
    draft = RDMDraft.create(minimal_record).commit()

    # Dumping should return dereferenced representation
    dump = draft.dumps()
    assert dump["metadata"]["subjects"] == [
        {
            "id": "http://id.nlm.nih.gov/mesh/A-D000007",
            "subject": "Abdominal Injuries",
            "@v": f"{running_app.subject_v._record.id}::1",
            "scheme": "MeSH",
        }
    ]
    # NOTE/WARNING: draft.dumps() modifies the draft too
    assert draft["metadata"]["subjects"] == [
        {
            "id": "http://id.nlm.nih.gov/mesh/A-D000007",
            "subject": "Abdominal Injuries",
            "@v": f"{running_app.subject_v._record.id}::1",
            "scheme": "MeSH",
        }
    ]

    # Loading draft again should produce an identical record.
    loaded_draft = RDMDraft.loads(dump)
    assert dict(draft) == dict(loaded_draft)

    # Calling commit() should clear the dereferenced relation.
    draft.commit()
    assert draft["metadata"]["subjects"] == [
        {"id": "http://id.nlm.nih.gov/mesh/A-D000007"}
    ]

    # subjects should be reachable through relations
    subject = next(draft.relations.subjects())
    assert "http://id.nlm.nih.gov/mesh/A-D000007" == subject["id"]
