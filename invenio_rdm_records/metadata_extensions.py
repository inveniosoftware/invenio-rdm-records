# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Metadata Extensions."""
from copy import deepcopy

from flask import current_app
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import Schema
from marshmallow.fields import Bool, Integer, List


class MetadataExtensions(object):
    """Custom metadata extensions helper class."""

    def __init__(self, extensions):
        """Constructor.

        :param extensions: `RDM_RECORDS_METADATA_EXTENSIONS` dict

        Example:
        {
            'dwc': {
                'family': {
                    'types': {
                        'marshmallow': SanitizedUnicode(),
                        'elasticsearch': 'keyword',
                    }
                },
                'genus': {
                    'types': {
                        'marshmallow': SanitizedUnicode(),
                        'elasticsearch': 'keyword',
                    }
                },
                'behavior': {
                    'types': {
                        'marshmallow': SanitizedUnicode(),
                        'elasticsearch': 'text',
                    }
                }
            }
        }

        Note: use translation layer `_()` to get human readable label from
              ids used internally.
        """
        self.extensions = deepcopy(extensions) or {}
        self._validate()

    def _validate(self):
        """Validates extension configuration.

        We only allow certain types, so this private method flags divergence
        from what is allowed early.
        """
        def validate_marshmallow_type(types):
            """Make sure the Marshmallow type is one we support."""
            def validate_basic_marshmallow_type(_type):
                allowed_types = [
                    Bool, DateString, Integer, SanitizedUnicode
                ]
                assert any([
                    isinstance(_type, allowed_type) for allowed_type
                    in allowed_types
                ])

            marshmallow_type = types['marshmallow']
            if isinstance(marshmallow_type, List):
                validate_basic_marshmallow_type(marshmallow_type.inner)
            else:
                validate_basic_marshmallow_type(marshmallow_type)

        def validate_elasticsearch_type(types):
            """Make sure the Elasticsearch type is one we support."""
            allowed_types = [
                'boolean', 'date', 'long', 'keyword', 'text'
            ]
            assert types['elasticsearch'] in allowed_types

        for section_key, section_cfg in self.extensions.items():
            for field_key, field_cfg in section_cfg.items():
                validate_marshmallow_type(field_cfg['types'])
                validate_elasticsearch_type(field_cfg['types'])

    def to_schema(self):
        """Dynamically creates and returns the extensions Schema."""
        schema_dict = {}

        for section_key, section_cfg in self.extensions.items():
            for field_key, field_cfg in section_cfg.items():
                key = "{}:{}".format(section_key, field_key)
                schema_dict[key] = field_cfg['types']['marshmallow']

        return Schema.from_dict(schema_dict)

    def get_field_type(self, field_key, _type):
        """Returns type value for given field_key and type.

        :params field_key: str formatted as <section_id>:<field_id>
        :params _type: str between 'elasticsearch' or 'marshmallow'
        """
        section_key, field_key = field_key.split(":", 1)
        return (
            self.extensions
                .get(section_key, {})
                .get(field_key, {})
                .get('types', {})
                .get(_type)
        )


def add_es_metadata_extensions(record_dict):
    """Add 'extensions_X' fields to record_dict prior to Elasticsearch index.

    :param record_dict: dumped Record dict
    """
    current_app_metadata_extensions = (
        current_app.extensions['invenio-rdm-records'].metadata_extensions
    )

    for key, value in record_dict.get('extensions', {}).items():
        field_type = current_app_metadata_extensions.get_field_type(
            key, 'elasticsearch'
        )
        if not field_type:
            continue

        es_field = 'extensions_{}s'.format(field_type)

        if es_field not in record_dict:
            record_dict[es_field] = []

        record_dict[es_field].append({'key': key, 'value': value})
