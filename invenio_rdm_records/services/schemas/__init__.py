# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from functools import partial

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records.schema import RecordSchema
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from marshmallow import EXCLUDE, ValidationError, fields, post_dump
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin

from .access import AccessSchema
from .files import FilesSchema
from .metadata import MetadataSchema
from .parent import RDMParentSchema
from .pids import PIDSchema
from .versions import VersionsSchema


def validate_scheme(scheme):
    """Validate a PID scheme."""
    if scheme not in current_app.config["RDM_PERSISTENT_IDENTIFIERS"]:
        raise ValidationError(_("Invalid persistent identifier scheme."))


class RDMRecordSchema(RecordSchema, FieldPermissionsMixin):
    """Record schema."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    field_load_permissions = {
        "files": "update_draft",
    }

    # ATTENTION: In this schema you should be using the ``NestedAttribute``
    # instead  of Marshmallow's ``fields.Nested``. Using NestedAttribute
    # ensures that the nested schema will receive the system field instead of
    # the record dict (i.e. record.myattr instead of record['myattr']).

    pids = fields.Dict(
        keys=SanitizedUnicode(validate=validate_scheme),
        values=fields.Nested(PIDSchema),
    )
    metadata = NestedAttribute(MetadataSchema)
    custom_fields = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="RDM_CUSTOM_FIELDS")
    )
    # tombstone
    # provenance
    access = NestedAttribute(AccessSchema)
    files = NestedAttribute(FilesSchema)
    # notes = fields.List(fields.Nested(InternalNoteSchema))
    revision = fields.Integer(dump_only=True)
    versions = NestedAttribute(VersionsSchema, dump_only=True)
    parent = NestedAttribute(RDMParentSchema)
    is_published = fields.Boolean(dump_only=True)
    status = fields.String(dump_only=True)

    # stats = NestedAttribute(StatsSchema, dump_only=True)
    # schema_version = fields.Interger(dump_only=True)

    @post_dump
    def default_nested(self, data, many, **kwargs):
        """Serialize fields as empty dict for partial drafts.

        Cannot use marshmallow for Nested fields due to issue:
        https://github.com/marshmallow-code/marshmallow/issues/1566
        https://github.com/marshmallow-code/marshmallow/issues/41
        and more.
        """
        if not data.get("metadata"):
            data["metadata"] = {}
        if not data.get("pids"):
            data["pids"] = {}
        if not data.get("custom_fields"):
            data["custom_fields"] = {}

        return data


__all__ = (
    "RDMParentSchema",
    "RDMRecordSchema",
)
