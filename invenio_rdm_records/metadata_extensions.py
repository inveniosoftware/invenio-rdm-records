# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Metadata Extensions."""
from copy import deepcopy

from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import Schema
from marshmallow.fields import Float, Integer, List, Nested


class MetadataExtensions(object):
    """Custom metadata extensions helper class."""

    def __init__(self, extensions):
        """Constructor.

        :param extensions: `RDM_RECORDS_METADATA_EXTENSIONS` dict

        Example:
        {
            'dwc:Darwin Core': {
                'family:Family': {
                    'types': {
                        'marshmallow': SanitizedUnicode(),
                        'elasticsearch': 'keyword',
                    }
                },
                'genus:Genus': {
                    'types': {
                        'marshmallow': SanitizedUnicode(),
                        'elasticsearch': 'keyword',
                    }
                },
                'behavior:Behaviour': {
                    'types': {
                        'marshmallow': SanitizedUnicode(),
                        'elasticsearch': 'text',
                    }
                }
            }
        }
        """
        self.extensions = deepcopy(extensions) or {}
        self._validate()

    def _get_id(self, key):
        identifier, _ = key.split(":", 1)
        return identifier

    def _get_label(self, key):
        _, label = key.split(":", 1)
        return label

    def _validate(self):
        """Validates extension configuration.

        We only allow certain types, so this flags divergence from
        what is allowed early.
        """
        def validate_key(key):
            identifier, label = key.split(":", 1)
            assert identifier
            assert label

        def validate_marshmallow_type(types):
            """Make sure the Marshmallow type is one we support."""
            def validate_basic_marshmallow_type(_type):
                allowed_types = [
                    DateString, Float, Integer, SanitizedUnicode
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
                'date', 'double', 'long', 'keyword', 'text'
            ]
            assert types['elasticsearch'] in allowed_types

        section_ids = set()
        for section_key, section_cfg in self.extensions.items():
            validate_key(section_key)

            section_id = self._get_id(section_key)
            assert section_id not in section_ids
            section_ids.add(section_id)

            field_ids = set()
            for field_key, field_cfg in section_cfg.items():
                validate_key(field_key)

                field_id = self._get_id(field_key)
                assert field_id not in field_ids
                field_ids.add(field_id)

                validate_marshmallow_type(field_cfg['types'])
                validate_elasticsearch_type(field_cfg['types'])

    def to_schema(self):
        """Dynamically creates and returns the extensions Schema."""
        def schema_key(section_key, field_key):
            return "{}:{}".format(
                self._get_id(section_key), self._get_id(field_key),
            )

        schema_dict = {}
        for section_key, section_cfg in self.extensions.items():
            for field_key, field_cfg in section_cfg.items():
                key = schema_key(section_key, field_key)
                schema_dict[key] = field_cfg['types']['marshmallow']

        return Schema.from_dict(schema_dict)
