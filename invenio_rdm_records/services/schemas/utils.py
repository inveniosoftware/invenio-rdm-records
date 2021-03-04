# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schema utilities."""

import arrow
from arrow.parser import ParserError
from marshmallow import Schema, ValidationError, fields, missing
from marshmallow.schema import SchemaMeta
from marshmallow_utils.fields import NestedAttribute

from ...vocabularies import Vocabularies


def validate_entry(vocabulary_key, entry_key):
    """Validates if an entry is valid for a vocabulary.

    :param vocabulary_key: str, Vocabulary key
    :param entry_key: str, specific entry key

    raises marshmallow.ValidationError if entry is not valid.
    """
    vocabulary = Vocabularies.get_vocabulary(vocabulary_key)
    obj = vocabulary.get_entry_by_dict(entry_key)
    if not obj:
        raise ValidationError(
            vocabulary.get_invalid(entry_key)
        )


def dump_empty(schema_or_field):
    """Return a full json-compatible dict with empty values.

    NOTE: This is only needed because the frontend needs it.
          This might change soon.
    """
    if isinstance(schema_or_field, (Schema,)):
        schema = schema_or_field
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, SchemaMeta):
        # NOTE: Nested fields can pass a Schema class (SchemaMeta)
        #       or a Schema instance.
        #       Schema classes need to be instantiated to get .fields
        schema = schema_or_field()
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, fields.List):
        field = schema_or_field
        return [dump_empty(field.inner)]
    if isinstance(schema_or_field, NestedAttribute):
        field = schema_or_field
        return dump_empty(field.nested)

    return None
