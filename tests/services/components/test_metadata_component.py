# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service Metadata component."""

from flask_principal import Identity, UserNeed
from invenio_access.permissions import system_identity
from marshmallow import ValidationError

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.api import RDMDraft, RDMParent
from invenio_rdm_records.services import RDMRecordService
from invenio_rdm_records.services.components import MetadataComponent


def test_metadata_component(minimal_record, parent, identity_simple, location):
    """Test the metadata component."""
    record = RDMRecord.create(minimal_record, parent=parent)
    draft = RDMDraft.new_version(record)

    assert 'publication_date' in record.metadata
    assert 'title' in record.metadata

    component = MetadataComponent(RDMRecordService())
    component.new_version(identity_simple, draft=draft, record=record)

    # Make sure publication_date was NOT copied, but that title WAS copied
    assert 'publication_date' not in draft.metadata
    assert 'title' in draft.metadata

    # make sure the reference management is correct
    assert 'publication_date' in record.metadata
