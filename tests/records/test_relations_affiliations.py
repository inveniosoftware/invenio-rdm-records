# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record - affiliation relationships."""

import pytest
from invenio_db import db
from invenio_records.systemfields.relations import InvalidRelationValue
from jsonschema.exceptions import ValidationError

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


#
# Tests
#
def test_affiliations_field(running_app, minimal_record):
    """Affiliations should be defined as a relation."""
    assert "creator_affiliations" in RDMDraft.relations
    assert "contributor_affiliations" in RDMDraft.relations
    assert "creator_affiliations" in RDMRecord.relations
    assert "contributor_affiliations" in RDMRecord.relations
    assert RDMDraft.relations.contributor_affiliations
    assert RDMDraft.relations.creator_affiliations
    assert RDMRecord.relations.contributor_affiliations
    assert RDMRecord.relations.creator_affiliations


#
# Creator Affiliations
#
@pytest.fixture(scope="function")
def minimal_record_with_creator(minimal_record):
    minimal_record["metadata"]["creators"][0]["affiliations"] = [{"id": "cern"}]

    return minimal_record


def test_creator_affiliations_validation(running_app, minimal_record_with_creator):
    minimal_record = minimal_record_with_creator
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()

    # test it did not change
    creators = minimal_record_with_creator["metadata"]["creators"]
    affiliations = creators[0]["affiliations"]
    assert list(affiliations) == [{"id": "cern"}]

    # test it was saved properly
    aff = list(list(draft.relations.creator_affiliations())[0])[0]
    # since it is loaded it will contain more fields
    assert aff["id"] == "cern"


def test_creator_affiliations_with_name_validation(
    running_app, minimal_record_with_creator
):
    minimal_record = minimal_record_with_creator
    minimal_record["metadata"]["creators"][0]["affiliations"].append(
        {"name": "free-text"}
    )
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()

    # test it did not change
    creators = minimal_record_with_creator["metadata"]["creators"]
    affiliations = creators[0]["affiliations"]
    assert list(affiliations) == [{"id": "cern"}, {"name": "free-text"}]

    # Length should be only 1, since free-text should not be saved
    aff_list = list(list(draft.relations.creator_affiliations())[0])
    assert len(aff_list) == 1
    aff = aff_list[0]
    # since it is loaded it will contain more fields
    assert aff["id"] == "cern"


def test_creator_affiliations_with_name_cleanup_validation(running_app, minimal_record):
    minimal_record["metadata"]["creators"][0]["affiliations"] = [
        {"id": "cern", "name": "should-remove"}
    ]
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()

    # test it did not change
    creators = minimal_record["metadata"]["creators"]
    affiliations = creators[0]["affiliations"]
    assert list(affiliations) == [{"id": "cern"}]

    # test it was saved properly
    aff = list(list(draft.relations.creator_affiliations())[0])[0]
    # since it is loaded it will contain more fields
    assert aff["id"] == "cern"


def test_creator_affiliations_indexing(running_app, minimal_record_with_creator):
    minimal_record = minimal_record_with_creator
    draft = RDMDraft.create(minimal_record).commit()

    # Dump draft - dumps will dereference relations which inturn updates the
    # internal record dict so dump and record should be identical.
    dump = draft.dumps()
    assert dump["metadata"]["creators"][0]["affiliations"] == [
        {
            "id": "cern",
            "name": "CERN",
            "@v": f"{running_app.affiliations_v._record.id}::1",
        }
    ]

    # Load draft again - should produce an identical record.
    loaded_draft = RDMDraft.loads(dump)
    assert dict(draft) == dict(loaded_draft)

    # Calling commit() will clear the dereferenced relation.
    loaded_draft.commit()
    loaded_aff = loaded_draft["metadata"]["creators"][0]["affiliations"]
    assert loaded_aff == [{"id": "cern"}]


def test_creator_affiliations_invalid(running_app, minimal_record):
    """Should fail on invalid id's and invalid structure."""
    # The id "invalid" does not exists.
    minimal_record["metadata"]["creators"][0]["affiliations"] = [{"id": "invalid"}]
    pytest.raises(InvalidRelationValue, RDMDraft.create(minimal_record).commit)

    # Not a list of objects
    minimal_record["metadata"]["creators"][0]["affiliations"] = {"id": "cern"}
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # no additional keys are allowed
    minimal_record["metadata"]["creators"][0]["affiliations"] = [{"test": "cern"}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # non-string types are not allowed as id values
    minimal_record["metadata"]["creators"][0]["affiliations"] = [{"id": 1}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # No duplicates
    minimal_record["metadata"]["creators"][0]["affiliations"] = [
        {"id": "cern"},
        {"id": "cern"},
    ]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)


#
# Contributor Affiliations
#
@pytest.fixture(scope="function")
def minimal_record_with_contributor(minimal_record):
    creators = minimal_record["metadata"]["creators"]
    minimal_record["metadata"]["contributors"] = creators
    minimal_record["metadata"]["contributors"][0]["affiliations"] = [{"id": "cern"}]

    return minimal_record


def test_contributor_affiliations_validation(
    running_app, minimal_record_with_contributor
):
    minimal_record = minimal_record_with_contributor
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()

    # test it did not change
    contributors = minimal_record_with_contributor["metadata"]["contributors"]
    affiliations = contributors[0]["affiliations"]
    assert list(affiliations) == [{"id": "cern"}]

    # test it was saved properly
    aff = list(list(draft.relations.contributor_affiliations())[0])[0]
    # since it is loaded it will contain more fields
    assert aff["id"] == "cern"


def test_contributor_affiliations_indexing(
    running_app, minimal_record_with_contributor
):
    minimal_record = minimal_record_with_contributor
    draft = RDMDraft.create(minimal_record).commit()

    # Dump draft - dumps will dereference relations which inturn updates the
    # internal record dict so dump and record should be identical.
    dump = draft.dumps()
    assert dump["metadata"]["contributors"][0]["affiliations"] == [
        {
            "id": "cern",
            "name": "CERN",
            "@v": f"{running_app.affiliations_v._record.id}::1",
        }
    ]

    # Load draft again - should produce an identical record.
    loaded_draft = RDMDraft.loads(dump)
    assert dict(draft) == dict(loaded_draft)

    # Calling commit() will clear the dereferenced relation.
    loaded_draft.commit()
    loaded_aff = loaded_draft["metadata"]["contributors"][0]["affiliations"]
    assert loaded_aff == [{"id": "cern"}]


def test_contributor_affiliations_invalid(running_app, minimal_record_with_contributor):
    """Should fail on invalid id's and invalid structure."""
    minimal_record = minimal_record_with_contributor
    # The id "invalid" does not exists.
    minimal_record["metadata"]["contributors"][0]["affiliations"] = [{"id": "invalid"}]
    pytest.raises(InvalidRelationValue, RDMDraft.create(minimal_record).commit)

    # Not a list of objects
    minimal_record["metadata"]["contributors"][0]["affiliations"] = {"id": "cern"}
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # no additional keys are allowed
    minimal_record["metadata"]["contributors"][0]["affiliations"] = [{"test": "cern"}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # non-string types are not allowed as id values
    minimal_record["metadata"]["contributors"][0]["affiliations"] = [{"id": 1}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # No duplicates
    minimal_record["metadata"]["contributors"][0]["affiliations"] = [
        {"id": "cern"},
        {"id": "cern"},
    ]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)
