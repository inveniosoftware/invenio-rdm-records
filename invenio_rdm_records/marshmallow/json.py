# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
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
from .utils import api_link_for, validate_iso639_3


class AccessConditionSchemaV1(StrictKeysMixin):
    """Access condition."""

    condition = SanitizedUnicode()
    link_validity = SanitizedUnicode()


class CommunitySchemaV1(StrictKeysMixin):
    """Communities to which the record belongs to."""

    primary = SanitizedUnicode()
    secondary = fields.List(SanitizedUnicode())


class IdentifierSchemaV1(StrictKeysMixin):
    """Extra/Alternate identifiers of the record."""

    identifier = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)


class AffiliationSchemaV1(StrictKeysMixin):
    """Affiliation of a creator/contributor."""

    name = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)


class CreatorSchemaV1(StrictKeysMixin):
    """Creator schema."""

    name = SanitizedUnicode(required=True)
    type = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = fields.List(fields.Nested(IdentifierSchemaV1))
    affiliations = fields.List(fields.Nested(AffiliationSchemaV1))


class ContributorSchemaV1(CreatorSchemaV1):
    """Contributor schema."""

    ROLES = [
        "ContactPerson",
        "Researcher",
        "Other"
    ]

    role = SanitizedUnicode(required=True, validate=validate.OneOf(
                choices=ROLES,
                error=_('Invalid role. {input} not one of {choices}.')
            ))


class FilesSchemaV1(StrictKeysMixin):
    """Files metadata schema."""

    type = fields.String(required=True)
    checksum = fields.String(required=True)
    size = fields.Integer(required=True)
    bucket = fields.String(required=True)
    key = fields.String(required=True)
    links = fields.Method('get_links', required=True)

    def get_links(self, obj):
        """Get links."""
        return {
            'self': api_link_for(
                'object', bucket=obj['bucket'], key=obj['key'])
        }


class InternalNoteSchemaV1(StrictKeysMixin):
    """Internal notes shema."""

    user = SanitizedUnicode(required=True)
    note = SanitizedUnicode(required=True)
    timestamp = DateString(required=True)


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
    type = SanitizedUnicode(validate=validate.OneOf(
            choices=DESCRIPTION_TYPES,
            error=_('Invalid description type. {input} not one of {choices}.')
        ))
    lang = SanitizedUnicode(validate=validate_iso639_3)


class LicenseSchemaV1(StrictKeysMixin):
    """License schema."""

    license = SanitizedUnicode()
    uri = SanitizedUnicode()
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class SubjectSchemaV1(StrictKeysMixin):
    """Subject schema."""

    subject = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


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


class RelatedIdentifierSchemaV1(StrictKeysMixin):
    """Related identifier schema."""

    identifier = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)
    relation_type = SanitizedUnicode(required=True)
    resource_type = fields.Nested(ResourceTypeSchemaV1)


class ReferenceSchemaV1(StrictKeysMixin):
    """Reference schema."""

    reference_string = SanitizedUnicode()
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class PointSchemaV1(StrictKeysMixin):
    """Point schema."""

    lat = fields.Number()
    lon = fields.Number()


class LocationSchemaV1(StrictKeysMixin):
    """Location schema."""

    point = fields.Nested(PointSchemaV1)
    place = SanitizedUnicode(required=True)
    description = SanitizedUnicode()


class MetadataSchemaV1(StrictKeysMixin):
    """Schema for the record metadata."""

    # Administrative fields
    _visibility = fields.Bool(default=True)
    _visibility_files = fields.Bool(default=True)
    _embargo_date = DateString()
    _access_condition = fields.Nested(AccessConditionSchemaV1)
    _contact = SanitizedUnicode()
    _community = fields.Nested(CommunitySchemaV1)
    _owners = fields.List(fields.Integer(), validate=validate.Length(min=1),
                          dump_only=True, required=True)
    _created_by = DateString()
    _files = fields.List(fields.Nested(FilesSchemaV1(), dump_only=True))
    _default_preview = SanitizedUnicode()
    _internal_notes = fields.List(fields.Nested(InternalNoteSchemaV1))
    # Metadata fields
    resource_type = fields.Nested(ResourceTypeSchemaV1)
    identifiers = fields.Nested(IdentifierSchemaV1)
    creators = fields.List(Nested(CreatorSchemaV1, required=True))
    titles = fields.List(fields.Nested(TitleSchemaV1))
    descriptions = fields.List(fields.Nested(DescriptionSchemaV1))
    publication_date = DateString()
    licenses = fields.List(fields.Nested(LicenseSchemaV1))
    subjects = fields.List(fields.Nested(SubjectSchemaV1))
    language = SanitizedUnicode(validate=validate_iso639_3)
    dates = fields.List(fields.Nested(DateSchemaV1))
    version = SanitizedUnicode()
    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifierSchemaV1))
    references = fields.List(fields.Nested(ReferenceSchemaV1))
    locations = fields.List(fields.Nested(LocationSchemaV1))

    @pre_load()
    def preload_publicationdate(self, data):
        """Default publication date."""
        if 'publication_date' not in data:
            data['publication_date'] = arrow.utcnow().date().isoformat()

    @pre_load()
    def preload_access(self, data):
        """Load 'access' from data and convert to '_access'.

        WHY: StrictKeysMixin prevents the use of `load_from`. If/When amended,
             we can replace this by `load_from`.
        """
        if 'access' in data:
            # Purposefully overrides any prior '_access'
            data['_access'] = data.pop('access')

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
