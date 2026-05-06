# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service Metadata component."""

from datetime import date
from unittest.mock import patch

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.services.components import (
    CustomFieldsComponent,
    MetadataComponent,
)


def test_metadata_component(minimal_record, parent, identity_simple, location):
    """Test the metadata component."""
    record = RDMRecord.create(minimal_record, parent=parent)
    draft = RDMDraft.new_version(record)

    assert "publication_date" in record.metadata
    assert "title" in record.metadata

    original_publication_date = record.metadata["publication_date"]

    component = MetadataComponent(current_rdm_records.records_service)
    with patch(
        "invenio_rdm_records.services.components.metadata.datetime",
        **{"now.return_value.date.return_value": date(2030, 1, 2)},
    ):
        component.new_version(identity_simple, draft=draft, record=record)

    # publication_date is auto-populated with today's date (not copied),
    # while title IS copied from the original record
    assert draft.metadata["publication_date"] == "2030-01-02"
    assert draft.metadata["publication_date"] != original_publication_date
    assert "title" in draft.metadata

    # make sure the reference management is correct
    assert record.metadata["publication_date"] == original_publication_date


def test_custom_fields_component_new_version(minimal_record, parent, location):
    """Custom fields are copied verbatim, with no auto-populated fields."""
    minimal_record["custom_fields"] = {"some:field": "original value"}
    record = RDMRecord.create(minimal_record, parent=parent)
    draft = RDMDraft.new_version(record)

    component = CustomFieldsComponent(current_rdm_records.records_service)
    component.new_version(None, draft=draft, record=record)

    assert draft.custom_fields == {"some:field": "original value"}
