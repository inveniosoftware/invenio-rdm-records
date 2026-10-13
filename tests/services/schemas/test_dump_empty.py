# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Tests for dump_empty."""

from functools import partial

from marshmallow import Schema, fields
from marshmallow_utils.fields import NestedAttribute

from invenio_rdm_records.services.schemas.utils import dump_empty


class _InnerSchema(Schema):
    """A minimal schema, standing in for something like CustomFieldsSchema."""

    foo = fields.String()
    bar = fields.String()


class _OuterSchema(Schema):
    """A schema whose nested field is built via a factory (functools.partial).

    This mirrors how RDMRecordSchema defines ``custom_fields``:

        custom_fields = NestedAttribute(
            partial(CustomFieldsSchema, fields_var="RDM_CUSTOM_FIELDS")
        )
    """

    custom_fields = NestedAttribute(partial(_InnerSchema, only=("foo", "bar")))


def test_dump_empty_resolves_partial_wrapped_nested_schema():
    """A NestedAttribute wrapping a functools.partial factory.

    Regression test: dump_empty used to return None for such fields
    because functools.partial instances didn't match any of its
    isinstance checks (Schema, SchemaMeta, fields.List, NestedAttribute/
    fields.Nested), silently falling through to `return None`. This later
    crashed callers (e.g. records_ui's new_record()) that assume nested
    dict-like fields are always initialized as dicts, not None, when
    trying to set a default value inside them.
    """
    result = dump_empty(_OuterSchema())

    assert result["custom_fields"] is not None
    assert result["custom_fields"] == {"foo": None, "bar": None}
