# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata resource type schema."""

from copy import deepcopy

from flask_babelex import lazy_gettext as _

from invenio_rdm_records.services.schemas.metadata import MetadataSchema

from .test_utils import assert_raises_messages

# NOTE: test for a valid full resource type is included in test_metadata.py
#       when testing for a valid minimal metadata as a whole


def test_valid_type_and_subtype(minimal_metadata):
    # default minimal_metadata's resource type is image-photo
    expected_metadata = deepcopy(minimal_metadata)
    expected_metadata["creators"][0]["person_or_org"]["name"] = "Brown, Troy"

    assert expected_metadata == MetadataSchema().load(minimal_metadata)


def test_valid_no_subtype(minimal_metadata):
    # whether id represents a resource type with or without subtype should
    # not matter
    expected_metadata = deepcopy(minimal_metadata)
    expected_metadata["creators"][0]["person_or_org"]["name"] = "Brown, Troy"
    expected_metadata["resource_type"] = minimal_metadata["resource_type"] = {
        "id": "dataset"
    }

    assert expected_metadata == MetadataSchema().load(minimal_metadata)


def test_invalid_no_resource_type(minimal_metadata):
    minimal_metadata["resource_type"] = {}
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": {'id': ["Missing data for required field."]}}
    )

    del minimal_metadata["resource_type"]
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"resource_type": ["Missing data for required field."]}
    )
