# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records.schema import RecordSchema
from marshmallow import ValidationError, fields, post_dump, validates
from marshmallow_utils.fields import NestedAttribute
from marshmallow_utils.permissions import FieldPermissionsMixin
from marshmallow_utils.schemas import IdentifierSchema

from .access import AccessSchema
from .files import FilesSchema
from .metadata import MetadataSchema
from .parent import RDMParentSchema
from .pids import PIDSchema
from .versions import VersionsSchema


class RDMRecordSchema(RecordSchema, FieldPermissionsMixin):
    """Record schema."""

    field_load_permissions = {
        'files': 'update_draft',
    }

    # ATTENTION: In this schema you should be using the ``NestedAttribute``
    # instead  of Marshmallow's ``fields.Nested``. Using NestedAttribute
    # ensures that the nested schema will receive the system field instead of
    # the record dict (i.e. record.myattr instead of record['myattr']).

    pids = fields.Dict(keys=fields.String(), values=fields.Nested(PIDSchema))
    metadata = NestedAttribute(MetadataSchema)
    # ext = fields.Method('dump_extensions', 'load_extensions')
    # tombstone
    # provenance
    access = NestedAttribute(AccessSchema)
    files = NestedAttribute(FilesSchema)
    # notes = fields.List(fields.Nested(InternalNoteSchema))
    revision = fields.Integer(dump_only=True)
    versions = NestedAttribute(VersionsSchema, dump_only=True)
    parent = NestedAttribute(RDMParentSchema, dump_only=True)

    is_published = fields.Boolean(dump_only=True)

    # stats = NestedAttribute(StatsSchema, dump_only=True)
    # relations = NestedAttribute(RelationsSchema, dump_only=True)
    # schema_version = fields.Interger(dump_only=True)

    # def dump_extensions(self, obj):
    #     """Dumps the extensions value.

    #     :params obj: invenio_records_files.api.Record instance
    #     """
    #     current_app_metadata_extensions = (
    #         current_app.extensions['invenio-rdm-records'].metadata_extensions
    #     )
    #     ExtensionSchema = current_app_metadata_extensions.to_schema()
    #     return ExtensionSchema().dump(obj.get('extensions', {}))

    # def load_extensions(self, value):
    #     """Loads the 'extensions' field.

    #     :params value: content of the input's 'extensions' field
    #     """
    #     current_app_metadata_extensions = (
    #         current_app.extensions['invenio-rdm-records'].metadata_extensions
    #     )
    #     ExtensionSchema = current_app_metadata_extensions.to_schema()

    #     return ExtensionSchema().load(value)

    @validates("pids")
    def validate_pids(self, value):
        """Validates the keys of the pids are supported providers."""
        error_messages = []
        for scheme, pid_attrs in value.items():
            # The required flag applies to the identifier value
            # It won't fail for empty allowing the components to reserve one
            id_schema = IdentifierSchema(
                fail_on_unknown=True, identifier_required=True)
            try:
                id_schema.load({
                    "scheme": scheme,
                    "identifier": pid_attrs.get("identifier")
                })
            except ValidationError:
                # cannot raise in case more than one pid presents errors
                error_messages.append(
                    _(f"Invalid value for scheme {scheme}")
                )

        if error_messages:
            raise ValidationError(message=error_messages)

    @post_dump
    def default_nested(self, data, many, **kwargs):
        """Serialize metadata as empty dict for partial drafts.

        Cannot use marshmallow for Nested fields due to issue:
        https://github.com/marshmallow-code/marshmallow/issues/1566
        https://github.com/marshmallow-code/marshmallow/issues/41
        and more.
        """
        if not data.get("metadata"):
            data["metadata"] = {}

        return data


__all__ = (
    'RDMParentSchema',
    'RDMRecordSchema',
)
