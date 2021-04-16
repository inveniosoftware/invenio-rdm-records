# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Invenio RDM Records MetadataSchema."""

import pytest
from marshmallow import ValidationError
from marshmallow.fields import Bool, Integer, List
from marshmallow_utils.fields import ISODateString, SanitizedUnicode

from invenio_rdm_records.services.schemas.metadata import MetadataSchema
from invenio_rdm_records.services.schemas.metadata_extensions import \
    MetadataExtensions


@pytest.mark.skip()
def test_extensions(app, minimal_record):
    """Test metadata extensions schema."""
    # Setup metadata extensions
    RDM_RECORDS_METADATA_NAMESPACES = {
        'dwc': {
            '@context': 'https://example.com/dwc/terms'
        },
        'nubiomed': {
            '@context': 'https://example.com/nubiomed/terms'
        }
    }

    RDM_RECORDS_METADATA_EXTENSIONS = {
        'dwc:family': {
            'elasticsearch': 'keyword',
            'marshmallow': SanitizedUnicode(required=True)
        },
        'dwc:behavior': {
            'elasticsearch': 'text',
            'marshmallow': SanitizedUnicode()
        },
        'nubiomed:number_in_sequence': {
            'elasticsearch': 'long',
            'marshmallow': Integer()
        },
        'nubiomed:scientific_sequence': {
            'elasticsearch': 'long',
            'marshmallow': List(Integer())
        },
        'nubiomed:original_presentation_date': {
            'elasticsearch': 'date',
            'marshmallow': ISODateString()
        },
        'nubiomed:right_or_wrong': {
            'elasticsearch': 'boolean',
            'marshmallow': Bool()
        }
    }

    orig_metadata_extensions = (
        app.extensions['invenio-rdm-records'].metadata_extensions
    )

    app.extensions['invenio-rdm-records'].metadata_extensions = (
        MetadataExtensions(
            RDM_RECORDS_METADATA_NAMESPACES,
            RDM_RECORDS_METADATA_EXTENSIONS
        )
    )

    # Minimal if not absent
    valid_minimal = {
        'dwc:family': 'Felidae'
    }
    minimal_record['extensions'] = valid_minimal
    data = MetadataSchema().load(minimal_record)
    assert valid_minimal == data.get('extensions')

    # Full
    valid_full = {
        'dwc:family': 'Felidae',
        'dwc:behavior': 'Plays with yarn, sleeps in cardboard box.',
        'nubiomed:number_in_sequence': 3,
        'nubiomed:scientific_sequence': [1, 1, 2, 3, 5, 8],
        'nubiomed:original_presentation_date': '2019-02-14',
        'nubiomed:right_or_wrong': True,
    }
    minimal_record['extensions'] = valid_full
    data = MetadataSchema().load(minimal_record)
    assert valid_full == data.get('extensions')

    # Invalid
    invalid_number_in_sequence = {
        'dwc:family': 'Felidae',
        'nubiomed:scientific_sequence': [1, 'l', 2, 3, 5, 8],
    }
    minimal_record['extensions'] = invalid_number_in_sequence
    with pytest.raises(ValidationError):
        data = MetadataSchema().load(minimal_record)

    app.extensions['invenio-rdm-records'].metadata_extensions = (
        orig_metadata_extensions
    )


def test_full_metadata_schema(vocabulary_clear, full_metadata):
    """Test metadata schema."""
    # Test full attributes

    data = MetadataSchema().load(full_metadata)
    assert data == full_metadata


def test_minimal_metadata_schema(
        vocabulary_clear, minimal_metadata, expected_minimal_metadata):

    metadata = MetadataSchema().load(minimal_metadata)

    assert expected_minimal_metadata == metadata


def test_additional_field_raises(vocabulary_clear, minimal_metadata):

    minimal_metadata["foo"] = "FOO"

    with pytest.raises(ValidationError):
        MetadataSchema().load(minimal_metadata)
