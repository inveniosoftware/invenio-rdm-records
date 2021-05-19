# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record relationships."""

import pytest
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records.systemfields.relations import InvalidRelationValue
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from jsonschema.exceptions import ValidationError

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


#
# Tests
#
def test_languages_field(app, location, minimal_record):
    """Languages should be defined as a relation."""
    assert 'languages' in RDMDraft.relations
    assert 'languages' in RDMRecord.relations
    assert RDMDraft.relations.languages


def test_languages_validation(app, location, minimal_record, lang):
    """Test languages relationship."""
    minimal_record["metadata"]["languages"] = [{"id": "eng"}]
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()
    assert minimal_record["metadata"]["languages"] == [{"id": "eng"}]

    lang = list(draft.relations.languages())[0]
    assert isinstance(lang, Vocabulary)


def test_languages_indexing(app, location, minimal_record, lang):
    """Test languages relationship."""
    minimal_record["metadata"]["languages"] = [{"id": "eng"}]
    draft = RDMDraft.create(minimal_record).commit()

    # Dump draft - dumps will dereference relations which inturn updates the
    # internal record dict so dump and record should be identical.
    dump = draft.dumps()
    assert dump["metadata"]["languages"] == [{
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "@v": f"{lang._record.id}::1"
    }]

    # Load draft again - should produce an identical record.
    loaded_draft = RDMDraft.loads(dump)
    assert dict(draft) == dict(loaded_draft)

    # Calling commit() will clear the dereferenced relation.
    loaded_draft.commit()
    assert loaded_draft["metadata"]["languages"] == [{"id": "eng"}]


def test_languages_invalid(app, location, minimal_record):
    """Should fail on invalid id's and invalid structure."""
    # The id "invalid" does not exists.
    minimal_record["metadata"]["languages"] = [{"id": "invalid"}]
    pytest.raises(InvalidRelationValue, RDMDraft.create(minimal_record).commit)

    # Not a list of objects
    minimal_record["metadata"]["languages"] = {"id": "eng"}
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # no additional keys are allowed
    minimal_record["metadata"]["languages"] = [{"test": "eng"}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # id key is required
    minimal_record["metadata"]["languages"] = [{}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # non-string types are not allowed as id values
    minimal_record["metadata"]["languages"] = [{"id": 1}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # Extra keys are not allowed
    minimal_record["metadata"]["languages"] = [{"id": "eng", "title": "rm"}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)

    # No duplicates
    minimal_record["metadata"]["languages"] = [{"id": "eng"}, {"id": "eng"}]
    pytest.raises(ValidationError, RDMDraft.create, minimal_record)
