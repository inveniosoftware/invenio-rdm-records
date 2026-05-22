# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-FileCopyrightText: 2020-2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""RDM record schema utilities."""

from marshmallow import Schema, fields
from marshmallow.schema import SchemaMeta
from marshmallow_utils.fields import NestedAttribute


def dump_empty(schema_or_field):
    """Return a full json-compatible dict with empty values.

    NOTE: This is only needed because the frontend needs it.
          This might change soon.
    """
    if isinstance(schema_or_field, (Schema,)):
        schema = schema_or_field
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, SchemaMeta):
        # Nested fields can pass a Schema class (SchemaMeta)
        # or a Schema instance.
        # Schema classes need to be instantiated to get .fields
        schema = schema_or_field()
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, fields.List):
        field = schema_or_field
        return [dump_empty(field.inner)]
    if isinstance(schema_or_field, (NestedAttribute, fields.Nested)):
        field = schema_or_field
        return dump_empty(field.nested)

    return None
