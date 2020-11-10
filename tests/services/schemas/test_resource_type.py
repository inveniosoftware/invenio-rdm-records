# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata resource type schema."""

import os

import pytest
from flask_babelex import lazy_gettext as _
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import ResourceTypeSchema

from .test_utils import assert_raises_messages


def test_valid_full(vocabulary_clear):
    valid_full = {
        "type": "image",
        "subtype": "image-photo"
    }
    assert valid_full == ResourceTypeSchema().load(valid_full)


def test_valid_no_subtype(vocabulary_clear):
    valid_no_subtype = {
        "type": "poster"
    }
    assert valid_no_subtype == ResourceTypeSchema().load(valid_no_subtype)


def test_invalid_no_type(vocabulary_clear):
    invalid_no_type = {
        "subtype": "image-photo"
    }

    assert_raises_messages(
        lambda: ResourceTypeSchema().load(invalid_no_type),
        {"type": ["Missing data for required field."]}
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


def test_invalid_type(custom_config, vocabulary_clear):
    # doubles as a test of custom config
    invalid_type = {
        "type": "invalid",
        "subtype": "image-photo"
    }

    assert_raises_messages(
        lambda: ResourceTypeSchema().load(invalid_type),
        {
            "type": [_(
                "Invalid value. Choose one of ['my_image', 'publication', "
                "'software']."
            )]
        }
    )


def test_invalid_subtype(custom_config, vocabulary_clear):
    invalid_subtype = {
        "type": "my_image",
        "subtype": "invalid"
    }

    assert_raises_messages(
        lambda: ResourceTypeSchema().load(invalid_subtype),
        {
            "subtype": [_(
                "Invalid value. Choose one of ['my_photo']."
            )]
        }
    )


def test_custom_valid_full(custom_config, vocabulary_clear):
    # new resource type validates
    valid_full = {
        "type": "my_image",
        "subtype": "my_photo"
    }
    data = ResourceTypeSchema().load(valid_full)
    assert data == valid_full


def test_custom_default_now_invalid(custom_config, vocabulary_clear):
    now_invalid_subtype = {
        "type": "image",
        "subtype": "image-photo"
    }

    assert_raises_messages(
        lambda: ResourceTypeSchema().load(now_invalid_subtype),
        {
            "type": [_(
                "Invalid value. Choose one of ['my_image', 'publication', "
                "'software']."
            )]
        }
    )
