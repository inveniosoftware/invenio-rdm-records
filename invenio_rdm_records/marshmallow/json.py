# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from flask_babelex import lazy_gettext as _
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import ValidationError, fields, missing, validate, \
    validates_schema

from ..models import AccessRight, ObjectType


class AccessSchemaV1(StrictKeysMixin):
    """Access schema."""

    # TODO revist acccording to
    # https://github.com/inveniosoftware/invenio-rdm-records/issues/20
    metadata_restricted = fields.Bool(required=True)
    files_restricted = fields.Bool(required=True)


class PersonIdsSchemaV1(StrictKeysMixin):
    """Ids schema."""

    source = SanitizedUnicode()
    value = SanitizedUnicode()


class ContributorSchemaV1(StrictKeysMixin):
    """Contributor schema."""

    ids = fields.Nested(PersonIdsSchemaV1, many=True)
    name = SanitizedUnicode(required=True)
    role = SanitizedUnicode()
    affiliations = fields.List(SanitizedUnicode())
    email = fields.Email()


class ResourceTypeSchemaV1(StrictKeysMixin):
    """Resource type schema."""

    type = fields.Str(
        required=True,
        error_messages=dict(
            required=_('Type must be specified.')
        ),
    )
    subtype = fields.Str()
    openaire_subtype = fields.Str()
    title = fields.Method('get_title', dump_only=True)

    def get_title(self, obj):
        """Get title."""
        obj = ObjectType.get_by_dict(obj)
        return obj['title']['en'] if obj else missing

    @validates_schema
    def validate_data(self, data):
        """Validate resource type."""
        obj = ObjectType.get_by_dict(data)
        if obj is None:
            raise ValidationError(_('Invalid resource type.'))

    def dump_openaire_type(self, obj):
        """Get OpenAIRE subtype."""
        acc = obj.get('access_right')
        if acc:
            return AccessRight.as_category(acc)
        return missing


class TitleSchemaV1(StrictKeysMixin):
    """Schema for the additional title."""

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    # TODO: Shall it be checked against the enum?
    title_type = SanitizedUnicode()
    lang = SanitizedUnicode()


class DescriptionSchemaV1(StrictKeysMixin):
    """Schema for the additional descriptions."""

    description = SanitizedUnicode(required=True,
                                   validate=validate.Length(min=3))
    # TODO: Shall it be checked against the enum?
    description_type = SanitizedUnicode()
    lang = SanitizedUnicode()


class MetadataSchemaV1(StrictKeysMixin):
    """Schema for the record metadata."""

    # TODO: Check enumeration (i.e. only open/embargoed/... accepted)
    access_right = SanitizedUnicode(required=True)
    access = fields.Nested(AccessSchemaV1)
    additional_descriptions = fields.List(fields.Nested(DescriptionSchemaV1))
    additional_titles = fields.List(fields.Nested(TitleSchemaV1))
    recid = PersistentIdentifier()
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    description = SanitizedUnicode()
    owners = fields.List(fields.Integer(),
                         validate=validate.Length(min=1),
                         required=True)
    keywords = fields.List(SanitizedUnicode(), many=True)
    publication_date = DateString()
    contributors = Nested(ContributorSchemaV1, many=True, required=True)
    resource_type = fields.Nested(ResourceTypeSchemaV1)


class RecordSchemaV1(StrictKeysMixin):
    """Record schema."""

    # TODO: Use `RecordMetadataSchemaJSONV1` to inject PID in PUT/PATCH/...
    metadata = fields.Nested(MetadataSchemaV1)
    bucket = fields.Str()
    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier(attribute='pid.pid_value')
