# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021-2023 TU Wien.
# Copyright (C) 2021-2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from functools import partial

from flask import current_app
from invenio_drafts_resources.services.records.schema import RecordSchema
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from marshmallow import EXCLUDE, ValidationError, fields, post_dump
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin

from .access import AccessSchema
from .files import FilesSchema
from .metadata import MetadataSchema
from .parent import RDMParentSchema
from .pids import PIDSchema
from .stats import StatsSchema
from .tombstone import DeletionStatusSchema, TombstoneSchema
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
    # provenance
    access = NestedAttribute(AccessSchema)
    files = NestedAttribute(FilesSchema)
    media_files = NestedAttribute(FilesSchema)
    # notes = fields.List(fields.Nested(InternalNoteSchema))
    revision = fields.Integer(dump_only=True)
    versions = NestedAttribute(VersionsSchema, dump_only=True)
    parent = NestedAttribute(RDMParentSchema)
    is_published = fields.Boolean(dump_only=True)
    status = fields.String(dump_only=True)

    tombstone = fields.Nested(TombstoneSchema, dump_only=True)
    deletion_status = fields.Nested(DeletionStatusSchema, dump_only=True)

    stats = NestedAttribute(StatsSchema, dump_only=True)
    # schema_version = fields.Integer(dump_only=True)

    def default_nested(self, data):
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

    def hide_tombstone(self, data):
        """Hide tombstone info if the record isn't deleted and metadata if it is."""
        is_deleted = (data.get("deletion_status") or {}).get("is_deleted", False)
        tombstone_visible = (data.get("tombstone") or {}).get("is_visible", True)

        if not is_deleted or not tombstone_visible:
            data.pop("tombstone", None)

        return data

    @post_dump
    def post_dump(self, data, many, **kwargs):
        """Perform some updates on the dumped data."""
        data = self.default_nested(data)
        data = self.hide_tombstone(data)
        return data
