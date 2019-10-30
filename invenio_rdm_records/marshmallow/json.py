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

import arrow
from flask_babelex import lazy_gettext as _
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import ValidationError, fields, pre_load, validate, \
    validates, validates_schema

from ..models import ObjectType
from .utils import validate_iso639_3


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

    ROLES = [
        "ContactPerson",
        "Researcher",
        "Other"
    ]

    ids = fields.Nested(PersonIdsSchemaV1, many=True)
    name = SanitizedUnicode(required=True)
    role = SanitizedUnicode(
        validate=validate.OneOf(
            choices=ROLES,
            error=_('Invalid role. {input} not one of {choices}.')
        ))
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

    @validates_schema
    def validate_data(self, data):
        """Validate resource type."""
        obj = ObjectType.get_by_dict(data)
        if obj is None:
            raise ValidationError(_('Invalid resource type.'))


class TitleSchemaV1(StrictKeysMixin):
    """Schema for the additional title."""

    TITLE_TYPES = [
          "AlternativeTitle",
          "Subtitle",
          "TranslatedTitle",
          "Other"
    ]

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    title_type = SanitizedUnicode(validate=validate.OneOf(
            choices=TITLE_TYPES,
            error=_('Invalid title type. {input} not one of {choices}.')
        ))
    lang = SanitizedUnicode(validate=validate_iso639_3)


class DescriptionSchemaV1(StrictKeysMixin):
    """Schema for the additional descriptions."""

    DESCRIPTION_TYPES = [
          "Abstract",
          "Methods",
          "SeriesInformation",
          "TableOfContents",
          "TechnicalInfo",
          "Other"
    ]
    description = SanitizedUnicode(required=True,
                                   validate=validate.Length(min=3))
    description_type = SanitizedUnicode(validate=validate.OneOf(
            choices=DESCRIPTION_TYPES,
            error=_('Invalid description type. {input} not one of {choices}.')
        ))
    lang = SanitizedUnicode(validate=validate_iso639_3)


class DateSchemaV1(StrictKeysMixin):
    """Schema for date intervals."""

    DATE_TYPES = [
        "Collected",
        "Valid",
        "Withdrawn"
    ]

    start = DateString()
    end = DateString()
    type = fields.Str(required=True, validate=validate.OneOf(
            choices=DATE_TYPES,
            error=_('Invalid date type. {input} not one of {choices}.')
        ))
    description = fields.Str()


class RightSchemaV1(StrictKeysMixin):
    """Schema for rights."""

    rights = SanitizedUnicode()
    uri = SanitizedUnicode()
    identifier = SanitizedUnicode()
    identifier_scheme = SanitizedUnicode()
    scheme_uri = SanitizedUnicode()
    lang = SanitizedUnicode(validate=validate_iso639_3)


class MetadataSchemaV1(StrictKeysMixin):
    """Schema for the record metadata."""

    # TODO: Check enumeration (i.e. only open/embargoed/... accepted)
    access_right = SanitizedUnicode(required=True)
    access = fields.Nested(AccessSchemaV1)
    additional_descriptions = fields.List(fields.Nested(DescriptionSchemaV1))
    additional_titles = fields.List(fields.Nested(TitleSchemaV1))
    contributors = Nested(ContributorSchemaV1, many=True, required=True)
    dates = fields.List(
        fields.Nested(DateSchemaV1), validate=validate.Length(min=1))
    description = SanitizedUnicode()
    embargo_date = DateString()
    keywords = fields.List(SanitizedUnicode(), many=True)
    language = SanitizedUnicode(validate=validate_iso639_3)
    owners = fields.List(fields.Integer(),
                         validate=validate.Length(min=1),
                         required=True)
    publication_date = DateString()
    recid = PersistentIdentifier()
    resource_type = fields.Nested(ResourceTypeSchemaV1)
    rights = fields.List(fields.Nested(RightSchemaV1))
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    version = SanitizedUnicode()

    @pre_load()
    def preload_publicationdate(self, data):
        """Default publication date."""
        if 'publication_date' not in data:
            data['publication_date'] = arrow.utcnow().date().isoformat()

    @validates('dates')
    def validate_dates(self, value):
        """Validate that start date is before the corresponding end date."""
        for interval in value:
            start = arrow.get(interval.get('start'), 'YYYY-MM-DD').date() \
                if interval.get('start') else None
            end = arrow.get(interval.get('end'), 'YYYY-MM-DD').date() \
                if interval.get('end') else None

            if not start and not end:
                raise ValidationError(
                    _('There must be at least one date.'),
                    field_names=['dates']
                )
            if start and end and start > end:
                raise ValidationError(
                    _('"start" date must be before "end" date.'),
                    field_names=['dates']
                )

    @validates('embargo_date')
    def validate_embargo_date(self, value):
        """Validate that embargo date is in the future."""
        if arrow.get(value).date() <= arrow.utcnow().date():
            raise ValidationError(
                _('Embargo date must be in the future.'),
                field_names=['embargo_date']
            )


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
