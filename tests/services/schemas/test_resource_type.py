# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata resource type schema."""

import os
from copy import deepcopy

import pytest
from flask_babelex import lazy_gettext as _
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema

from .test_utils import assert_raises_messages

# NOTE: test for a valid full resource type is included in test_metadata.py
#       when testing for a valid minimal metadata as a whole


def test_valid_no_subtype(minimal_metadata, vocabulary_clear):
    expected_metadata = deepcopy(minimal_metadata)
    expected_metadata["creators"][0]["person_or_org"]["name"] = "Brown, Troy"
    expected_metadata["resource_type"] = minimal_metadata["resource_type"] = {
        "type": "poster"
    }

    assert expected_metadata == MetadataSchema().load(minimal_metadata)


def test_invalid_no_resource_type(minimal_metadata, vocabulary_clear):
    minimal_metadata["resource_type"] = {}
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": ["Missing data for required field."]}
    )

    del minimal_metadata["resource_type"]
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": ["Missing data for required field."]}
    )


def test_invalid_no_type(minimal_metadata, vocabulary_clear):
    minimal_metadata["resource_type"] = {"subtype": "image-photo"}

    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": ["Missing data for required field."]}
    )


@pytest.fixture
def custom_config(config):
    prev_custom_vocabularies = config['RDM_RECORDS_CUSTOM_VOCABULARIES']

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'resource_type': {
            'path': os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data',
                'resource_types.csv'
            )
        }
    }

    yield config

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_custom_vocabularies


def test_invalid_type(custom_config, minimal_metadata, vocabulary_clear):
    # doubles as a test of custom config
    minimal_metadata["resource_type"] = {
        "type": "invalid",
        "subtype": "image-photo"
    }

    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": [_("Invalid value.")]}
    )


def test_invalid_subtype(custom_config, minimal_metadata, vocabulary_clear):
    minimal_metadata["resource_type"] = {
        "type": "my_image",
        "subtype": "invalid"
    }

    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": [_("Invalid value.")]}
    )


def test_custom_valid_full(custom_config, minimal_metadata, vocabulary_clear):
    expected_metadata = deepcopy(minimal_metadata)
    expected_metadata["creators"][0]["person_or_org"]["name"] = "Brown, Troy"
    expected_metadata["resource_type"] = minimal_metadata["resource_type"] = {
        "type": "my_image",
        "subtype": "my_photo"
    }

    assert expected_metadata == MetadataSchema().load(minimal_metadata)


def test_custom_previous_types_now_invalid(
        custom_config, minimal_metadata, vocabulary_clear):
    minimal_metadata["resource_type"] = {
        "type": "image",
        "subtype": "image-photo"
    }

    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": [_("Invalid value.")]}
    )
