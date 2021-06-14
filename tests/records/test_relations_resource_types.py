# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
# Copyright (C) 2021 Northwestern University
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record relationships."""

import pytest
from invenio_db import db
from invenio_records.systemfields.relations import InvalidRelationValue

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


#
# Tests
#
def test_resource_types_field(running_app):
    assert 'resource_type' in RDMDraft.relations
    assert 'resource_type' in RDMRecord.relations
    assert RDMDraft.relations.resource_type
    assert RDMRecord.relations.resource_type


def test_resource_type_validation(running_app, minimal_record):
    """Tests data content validation."""
    # Valid id
    minimal_record["metadata"]["resource_type"] = {"id": "image-photo"}

    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()

    assert draft["metadata"]["resource_type"] == {"id": "image-photo"}

    # Invalid id
    minimal_record["metadata"]["resource_type"] = {"id": "invalid"}

    pytest.raises(InvalidRelationValue, RDMDraft.create(minimal_record).commit)


def test_resource_types_indexing(running_app, minimal_record):
    """Test dereferencing characteristics/features really."""
    minimal_record["metadata"]["resource_type"] = {"id": "image-photo"}
    draft = RDMDraft.create(minimal_record).commit()

    # TODO/WARNING: draft.dumps() modifies draft
    dump = draft.dumps()
    assert dump["metadata"]["resource_type"] == {
        "id": "image-photo",
        "title": {"en": "Photo"},
        "@v": f"{running_app.resource_type_v._record.id}::1"
    }

    # Load draft again - should produce an identical record.
    loaded_draft = RDMDraft.loads(dump)
    assert dict(draft) == dict(loaded_draft)

    # Calling commit() will clear the dereferenced relation.
    loaded_draft.commit()
    assert loaded_draft["metadata"]["resource_type"] == {"id": "image-photo"}
