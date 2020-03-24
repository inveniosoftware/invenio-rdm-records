# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""
import time
from datetime import date

import arrow
from edtf.parser.grammar import level0Expression
from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_records_rest.schemas import Nested
from invenio_records_rest.schemas.fields import DateString, \
    PersistentIdentifier, SanitizedUnicode
from invenio_rest.serializer import BaseSchema
from marshmallow import ValidationError, fields, post_load, validate, \
    validates, validates_schema

from ..vocabularies import Vocabulary
from .fields import EDTFLevel0DateString
from .utils import api_link_for, validate_iso639_3


class CommunitySchemaV1(BaseSchema):
    """Communities to which the record belongs to."""

    primary = SanitizedUnicode(required=True)
    secondary = fields.List(SanitizedUnicode())


# 'Fake' Identifiers Field
def _not_blank(error_msg):
    """Returns a non-blank validation rule with custom error message."""
    return validate.Length(min=1, error=error_msg)


def Identifiers():
    """Returns a "fake" Identifiers field.

    Field expects:

        "<scheme1>": "<identifier1>",
        ...
        "<schemeN>": "<identifierN>"
    """
    return fields.Dict(
        # scheme
        keys=SanitizedUnicode(
            required=True, validate=_not_blank(_('Scheme cannot be blank.'))
        ),
        # identifier
        values=SanitizedUnicode(
            required=True,
            validate=_not_blank(_('Identifier cannot be blank.'))
        )
    )


class AffiliationSchemaV1(BaseSchema):
    """Affiliation of a creator/contributor."""

    name = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)


class CreatorSchemaV1(BaseSchema):
    """Creator schema."""

    NAMES = [
        "Organizational",
        "Personal"
    ]

    # TODO: Need to revisit `name` in Deposit form:
    #       current mock-up doesn't have `name` field, so there is assumed
    #       work on the front-end to fill this value.
    name = SanitizedUnicode(required=True)
    type = SanitizedUnicode(required=True, validate=validate.OneOf(
                choices=NAMES,
                error=_('Invalid name type. {input} not one of {choices}.')
            ))
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = Identifiers()
    affiliations = fields.List(fields.Nested(AffiliationSchemaV1))


class ContributorSchemaV1(CreatorSchemaV1):
    """Contributor schema."""

    ROLES = [
        "ContactPerson",
        "DataCollector",
        "DataCurator",
        "DataManager",
        "Distributor",
        "Editor",
        "HostingInstitution",
        "Producer",
        "ProjectLeader",
        "ProjectManager",
        "ProjectMember",
        "RegistrationAgency",
        "RegistrationAuthority",
        "RelatedPerson",
        "Researcher",
        "ResearchGroup",
        "RightsHolder",
        "Sponsor",
        "Supervisor",
        "WorkPackageLeader",
        "Other"
    ]

    role = SanitizedUnicode(required=True, validate=validate.OneOf(
                choices=ROLES,
                error=_('Invalid role. {input} not one of {choices}.')
            ))


class FilesSchemaV1(BaseSchema):
    """Files metadata schema."""

    type = fields.String()
    checksum = fields.String()
    size = fields.Integer()
    bucket = fields.String()
    key = fields.String()
    links = fields.Method('get_links')

    def get_links(self, obj):
        """Get links."""
        return {
            'self': api_link_for(
                'object', bucket=obj['bucket'], key=obj['key'])
        }


class InternalNoteSchemaV1(BaseSchema):
    """Internal note shema."""

    user = SanitizedUnicode(required=True)
    note = SanitizedUnicode(required=True)
    timestamp = DateString(required=True)


class ResourceTypeSchemaV1(BaseSchema):
    """Resource type schema."""

    type = fields.Str(
        required=True,
        error_messages=dict(
            required=_('Type must be specified.')
        )
    )
    subtype = fields.Str()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate resource type."""
        vocabulary = Vocabulary.get_vocabulary('resource_types')
        obj = vocabulary.get_by_dict(data)
        if not obj:
            raise ValidationError(vocabulary.get_invalid(data))


class TitleSchemaV1(BaseSchema):
    """Schema for the additional title."""

    TITLE_TYPES = [
        'MainTitle',
        "AlternativeTitle",
        "Subtitle",
        "TranslatedTitle",
        "Other"
    ]

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    type = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=TITLE_TYPES,
            error=_('Invalid title type. {input} not one of {choices}.')
        ), default='MainTitle')
    lang = SanitizedUnicode(validate=validate_iso639_3)


class DescriptionSchemaV1(BaseSchema):
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
    type = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=DESCRIPTION_TYPES,
            error=_('Invalid description type. {input} not one of {choices}.')
        ))
    lang = SanitizedUnicode(validate=validate_iso639_3)


class LicenseSchemaV1(BaseSchema):
    """License schema."""

    license = SanitizedUnicode(required=True)
    uri = SanitizedUnicode()
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class SubjectSchemaV1(BaseSchema):
    """Subject schema."""

    subject = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class DateSchemaV1(BaseSchema):
    """Schema for date intervals."""

    DATE_TYPES = [
        "Accepted",
        "Available",
        "Copyrighted",
        "Collected",
        "Created",
        "Issued",
        "Submitted",
        "Updated",
        "Valid",
        "Withdrawn",
        "Other"
    ]

    start = DateString()
    end = DateString()
    type = fields.Str(required=True, validate=validate.OneOf(
            choices=DATE_TYPES,
            error=_('Invalid date type. {input} not one of {choices}.')
        ))
    description = fields.Str()

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that start date is before the corresponding end date."""
        start = arrow.get(data.get('start'), 'YYYY-MM-DD').date() \
            if data.get('start') else None
        end = arrow.get(data.get('end'), 'YYYY-MM-DD').date() \
            if data.get('end') else None

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


class RelatedIdentifierSchemaV1(BaseSchema):
    """Related identifier schema."""

    RELATIONS = [
        "IsCitedBy",
        "Cites",
        "IsSupplementTo",
        "IsSupplementedBy",
        "IsContinuedBy",
        "Continues",
        "IsDescribedBy",
        "Describes",
        "HasMetadata",
        "IsMetadataFor",
        "HasVersion",
        "IsVersionOf",
        "IsNewVersionOf",
        "IsPreviousVersionOf",
        "IsPartOf",
        "HasPart",
        "IsReferencedBy",
        "References",
        "IsDocumentedBy",
        "Documents",
        "IsCompiledBy",
        "Compiles",
        "IsVariantFormOf",
        "IsOriginalFormOf",
        "IsIdenticalTo",
        "IsReviewedBy",
        "Reviews",
        "IsDerivedFrom",
        "IsSourceOf",
        "IsRequiredBy",
        "Requires",
        "IsObsoletedBy",
        "Obsoletes"
    ]

    SCHEMES = [
        "ARK",
        "arXiv",
        "bibcode",
        "DOI",
        "EAN13",
        "EISSN",
        "Handle",
        "IGSN",
        "ISBN",
        "ISSN",
        "ISTC",
        "LISSN",
        "LSID",
        "PMID",
        "PURL",
        "UPC",
        "URL",
        "URN",
        "w3id"
    ]

    identifier = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=SCHEMES,
            error=_('Invalid related identifier scheme. ' +
                    '{input} not one of {choices}.')
        ))
    relation_type = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=RELATIONS,
            error=_('Invalid relation type. {input} not one of {choices}.')
        ))
    resource_type = fields.Nested(ResourceTypeSchemaV1)


class ReferenceSchemaV1(BaseSchema):
    """Reference schema."""

    SCHEMES = [
        "ISNI",
        "GRID",
        "Crossref Funder ID",
        "Other"
    ]
    reference_string = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode(validate=validate.OneOf(
            choices=SCHEMES,
            error=_('Invalid reference scheme. {input} not one of {choices}.')
        ))


class PointSchemaV1(BaseSchema):
    """Point schema."""

    lat = fields.Number(required=True)
    lon = fields.Number(required=True)


class LocationSchemaV1(BaseSchema):
    """Location schema."""

    point = fields.Nested(PointSchemaV1)
    place = SanitizedUnicode(required=True)
    description = SanitizedUnicode()


class AccessSchemaV1(BaseSchema):
    """Access schema."""

    metadata_restricted = fields.Bool(required=True)
    files_restricted = fields.Bool(required=True)


def prepare_publication_date(record_dict):
    """
    Adds search and API compatible _publication_date_search field.

    This date is the lowest year-month-day date from the interval or (partial)
    date.

    WHY:
        - The regular publication_date is not in a format ES can use for
          powerful date queries.
        - Nor is it in a format serializers can use directly (more of a
          convenience in their case).
        - It supports our effort to align DB record and ES record.

    NOTE: Keeping this function outside the class to make it easier to move
          when dealing with deposit. By then, if only called here, it can
          be merged in MetadataSchemaV1.

    :param record_dict: loaded Record dict
    """
    parser = level0Expression("level0")
    date_or_interval = parser.parseString(record_dict['publication_date'])[0]
    # lower_strict() is available for EDTF Interval AND Date objects
    date_tuple = date_or_interval.lower_strict()
    record_dict['_publication_date_search'] = time.strftime(
        "%Y-%m-%d", date_tuple
    )


class MetadataSchemaV1(BaseSchema):
    """Schema for the record metadata."""

    # Administrative fields
    access_right = SanitizedUnicode(required=True, validate=validate.OneOf(
        choices=['open', 'embargoed', 'restricted', 'closed'],
        error=_('Invalid access right. {input} not one of {choices}.')
    ))
    _access = fields.Nested(AccessSchemaV1, required=True)
    _owners = fields.List(fields.Integer, validate=validate.Length(min=1),
                          required=True)
    _created_by = fields.Integer(required=True)
    _default_preview = SanitizedUnicode()
    _files = fields.List(fields.Nested(FilesSchemaV1(), dump_only=True))
    _internal_notes = fields.List(fields.Nested(InternalNoteSchemaV1))
    _embargo_date = DateString(data_key="embargo_date",
                               attribute="embargo_date")
    _community = fields.Nested(CommunitySchemaV1, data_key="community",
                               attribute="community")
    _contact = SanitizedUnicode(data_key="contact", attribute="contact")

    # Metadata fields
    identifiers = Identifiers()
    creators = fields.List(Nested(CreatorSchemaV1), required=True)
    titles = fields.List(fields.Nested(TitleSchemaV1), required=True)
    resource_type = fields.Nested(ResourceTypeSchemaV1, required=True)
    recid = PersistentIdentifier()
    publication_date = EDTFLevel0DateString(
        missing=lambda: date.today().isoformat()
    )
    subjects = fields.List(fields.Nested(SubjectSchemaV1))
    contributors = fields.List(Nested(ContributorSchemaV1))
    dates = fields.List(fields.Nested(DateSchemaV1))
    language = SanitizedUnicode(validate=validate_iso639_3)
    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifierSchemaV1))
    version = SanitizedUnicode()
    licenses = fields.List(fields.Nested(LicenseSchemaV1))
    descriptions = fields.List(fields.Nested(DescriptionSchemaV1))
    locations = fields.List(fields.Nested(LocationSchemaV1))
    references = fields.List(fields.Nested(ReferenceSchemaV1))
    extensions = fields.Method('dump_extensions', 'load_extensions')

    def dump_extensions(self, obj):
        """Dumps the extensions value.

        :params obj: content of the object's 'extensions' field
        """
        current_app_metadata_extensions = (
            current_app.extensions['invenio-rdm-records'].metadata_extensions
        )
        ExtensionSchema = current_app_metadata_extensions.to_schema()
        return ExtensionSchema().dump(obj)

    def load_extensions(self, value):
        """Loads the 'extensions' field.

        :params value: content of the input's 'extensions' field
        """
        current_app_metadata_extensions = (
            current_app.extensions['invenio-rdm-records'].metadata_extensions
        )
        ExtensionSchema = current_app_metadata_extensions.to_schema()

        return ExtensionSchema().load(value)

    @validates('_embargo_date')
    def validate_embargo_date(self, value):
        """Validate that embargo date is in the future."""
        if arrow.get(value).date() <= arrow.utcnow().date():
            raise ValidationError(
                _('Embargo date must be in the future.'),
                field_names=['embargo_date']
            )

    @post_load
    def post_load_publication_date(self, obj, **kwargs):
        """Add '_publication_date_search' field."""
        prepare_publication_date(obj)
        return obj


class RecordSchemaV1(BaseSchema):
    """Record schema."""

    # TODO: Use `RecordMetadataSchemaJSONV1` to inject PID in PUT/PATCH/...
    metadata = fields.Nested(MetadataSchemaV1)
    bucket = fields.Str()
    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier(attribute='pid.pid_value')
