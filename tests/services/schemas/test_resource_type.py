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
