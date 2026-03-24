# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service Metadata component."""

from copy import deepcopy

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.services.components.internal_notes import (
    InternalNotesComponent,
)


def test_notes_component(minimal_record, parent, identity_simple, location):
    """Test the metadata component."""
    record = RDMRecord.create(minimal_record, parent=parent)
    draft = RDMDraft.new_version(record)

    assert "publication_date" in record.metadata
    assert "title" in record.metadata

    component = InternalNotesComponent(current_rdm_records.records_service)
    new_data = deepcopy(draft)
    new_data["internal_notes"] = [{"note": "abc"}]
    # check if internal notes have correct attributes
    component.update_draft(identity_simple, data=new_data, record=draft)
    assert "internal_notes" in draft
    notes = draft["internal_notes"]
    assert "id" in notes[0]
    assert "timestamp" in notes[0]
    assert "added_by" in notes[0]

    # check if new internal note is added properly
    new_data["internal_notes"] = notes + [{"note": "def"}]
    component.update_draft(identity_simple, data=new_data, record=draft)
    assert "internal_notes" in draft
    updated_notes = draft["internal_notes"]
    assert len(updated_notes) == len(notes) + 1

    # check if internal note can be removed
    existing_id = updated_notes[0]["id"]
    del updated_notes[0]
    new_data["internal_notes"] = updated_notes
    component.update_draft(identity_simple, data=new_data, record=draft)
    assert "internal_notes" in draft
    updated_notes = draft["internal_notes"]
    assert len(updated_notes) == 1
    assert updated_notes[0]["id"] != existing_id

    # check if internal note can be removed and add another one
    existing_id = updated_notes[0]["id"]
    del updated_notes[0]
    new_data["internal_notes"] = updated_notes + [{"note": "def"}]
    component.update_draft(identity_simple, data=new_data, record=draft)
    assert "internal_notes" in draft
    updated_notes = draft["internal_notes"]
    assert len(updated_notes) == 1
    assert updated_notes[0]["id"] != existing_id

    # check if internal note once added, is immutable
    new_data["internal_notes"] = [
        {
            "note": "this text should not be taken into account",
            "id": updated_notes[0]["id"],
        }
    ]
    component.update_draft(identity_simple, data=new_data, record=draft)
    assert "internal_notes" in draft
    updated_notes = draft["internal_notes"]
    assert len(updated_notes) == 1
    assert updated_notes[0]["id"] == updated_notes[0]["id"]
    assert updated_notes[0]["note"] == "def"

    # test create
    record = RDMRecord.create(minimal_record, parent=parent)
    data = deepcopy(record)
    data["internal_notes"] = [{"note": "abc"}]
    component.create(identity_simple, data=data, record=record)
    assert "internal_notes" in record
    notes = record["internal_notes"]
    assert "id" in notes[0]
    assert "timestamp" in notes[0]
    assert "added_by" in notes[0]
    assert notes[0]["note"] == "abc"

    # test new version
    draft = RDMDraft.new_version(record)
    component.new_version(identity_simple, draft=draft, record=record)
    assert "internal_notes" in draft
    notes = draft["internal_notes"]
    assert "id" in notes[0]
    assert "timestamp" in notes[0]
    assert "added_by" in notes[0]
    assert notes[0]["note"] == "abc"

    # test publish
    record = RDMRecord.publish(draft)

    component.publish(identity_simple, draft=draft, record=record)
    assert "internal_notes" in record
    notes = record["internal_notes"]
    assert "id" in notes[0]
    assert "timestamp" in notes[0]
    assert "added_by" in notes[0]
    assert notes[0]["note"] == "abc"
