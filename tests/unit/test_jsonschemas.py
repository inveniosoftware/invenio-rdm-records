# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the jsonschema file itself.


It's the marshmallow tests that cover most cases. These tests are just
to make sure the jsonschema file syntax is correct and some of its basic
typing is enforced.
"""

import copy
import json
from os.path import abspath, dirname, join

import pytest
from jsonschema import ValidationError, validate

from invenio_rdm_records import jsonschemas


@pytest.fixture(scope='module')
def record_schema():
    jsonschemas_dir = abspath(dirname(jsonschemas.__file__))
    schema_path = join(jsonschemas_dir, 'records', 'record-v1.0.0.json')

    with open(schema_path) as schema_file:
        return json.load(schema_file)


@pytest.fixture(scope='function')
def subschema_for(record_schema):
    def _subschema(field, schema=record_schema):
        subschema = copy.deepcopy(schema)
        subschema.pop('required', None)
        properties = subschema.pop('properties')
        subschema['properties'] = {field: properties[field]}
        return subschema

    return _subschema


def test_valid_permissions(subschema_for):
    schema = subschema_for('sys')
    permissions = schema['properties']['sys']['properties']['permissions']
    schema['properties'] = {'permissions': permissions}
    data = {
        'permissions': {
            'can_read': [{'id': '1', 'type': 'person'}],
            'can_foo': [{'id': '2', 'type': 'org'}]
        }
    }

    assert validate(data, schema) is None  # means all good


def test_invalid_permissions(subschema_for):
    schema = subschema_for('sys')
    permissions = schema['properties']['sys']['properties']['permissions']
    schema['properties'] = {'permissions': permissions}
    data = {
        'permissions': {
            'can_read': 'baz'
        }
    }

    with pytest.raises(ValidationError):
        validate(data, schema)
