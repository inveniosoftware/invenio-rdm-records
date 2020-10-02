# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

import time

import arrow
import idutils
from edtf.parser.grammar import level0Expression
from flask import current_app
from flask_babelex import lazy_gettext as _
from marshmallow import INCLUDE, Schema, ValidationError, fields, post_load, \
    validate, validates, validates_schema
from marshmallow_utils.fields import EDTFDateString, GenFunction, \
    ISODateString, ISOLangString, SanitizedUnicode

from .utils import validate_entry

# TODO (Alex): This file can be split into separate parts for each group
#              of fields


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


class InternalNoteSchemaV1(Schema):
    """Internal note shema."""

    user = SanitizedUnicode(required=True)
    note = SanitizedUnicode(required=True)
    timestamp = ISODateString(required=True)


class DateSchemaV1(Schema):
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

    start = ISODateString()
    end = ISODateString()
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


class AffiliationSchemaV1(Schema):
    """Affiliation of a creator/contributor."""

    name = SanitizedUnicode(required=True)
    identifiers = fields.Dict()

    @validates("identifiers")
    def validate_identifiers(self, value):
        """Validate well-formed identifiers are passed."""
        if len(value) == 0:
            raise ValidationError(_("Invalid identifier."))

        if 'ror' in value:
            if not idutils.is_ror(value.get('ror')):
                raise ValidationError(_("Invalid identifier."))
        else:
            raise ValidationError(_("Invalid identifier."))


class CreatorSchemaV1(Schema):
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
    identifiers = fields.Dict()
    affiliations = fields.List(fields.Nested(AffiliationSchemaV1))

    @validates("identifiers")
    def validate_identifiers(self, value):
        """Validate well-formed identifiers are passed."""
        if any(key not in ['Orcid', 'ror'] for key in value.keys()):
            raise ValidationError(_("Invalid identifier."))

        if 'Orcid' in value:
            if not idutils.is_orcid(value.get('Orcid')):
                raise ValidationError(_("Invalid identifier."))

        if 'ror' in value:
            if not idutils.is_ror(value.get('ror')):
                raise ValidationError(_("Invalid identifier."))

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate identifier based on type."""
        if data['type'] == "Personal":
            person_identifiers = ['Orcid']
            identifiers = data.get('identifiers', {}).keys()
            if any([ident not in person_identifiers for ident in identifiers]):
                raise ValidationError(_("Invalid identifier for a person."))
        elif data['type'] == "Organizational":
            org_identifiers = ['ror']
            identifiers = data.get('identifiers', {}).keys()
            if any([ident not in org_identifiers for ident in identifiers]):
                raise ValidationError(
                    _("Invalid identifier for an organization.")
                )


class ContributorSchemaV1(CreatorSchemaV1):
    """Contributor schema."""

    role = SanitizedUnicode(required=True)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate role."""
        validate_entry('contributors.role', data)


class ResourceTypeSchemaV1(Schema):
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
        validate_entry('resource_type', data)


class TitleSchemaV1(Schema):
    """Schema for the additional title."""

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    type = SanitizedUnicode(missing='MainTitle')
    lang = ISOLangString()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate type."""
        validate_entry('titles.type', data)


class DescriptionSchemaV1(Schema):
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
    lang = ISOLangString()


class LicenseSchemaV1(Schema):
    """License schema."""

    license = SanitizedUnicode(required=True)
    uri = SanitizedUnicode()
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class SubjectSchemaV1(Schema):
    """Subject schema."""

    subject = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class DateSchemaV1(Schema):
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

    start = ISODateString()
    end = ISODateString()
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


class RelatedIdentifierSchemaV1(Schema):
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


class ReferenceSchemaV1(Schema):
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


class PointSchemaV1(Schema):
    """Point schema."""

    lat = fields.Number(required=True)
    lon = fields.Number(required=True)


class LocationSchemaV1(Schema):
    """Location schema."""

    point = fields.Nested(PointSchemaV1)
    place = SanitizedUnicode(required=True)
    description = SanitizedUnicode()


class MetadataSchemaV1(Schema):
    """Schema for the record metadata."""

    field_load_permissions = {
        # TODO: define "can_admin" action
        # '_internal_notes': 'admin',
    }

    field_dump_permissions = {
        # TODO: define "can_admin" action
        # '_internal_notes': 'admin',
    }

    class Meta:
        """Meta class to accept unknwon fields."""

        unknown = INCLUDE

    # Metadata fields
    titles = fields.List(fields.Nested(TitleSchemaV1), required=True)
    creators = fields.List(fields.Nested(CreatorSchemaV1), required=True)
    resource_type = fields.Nested(ResourceTypeSchemaV1, required=True)
    publication_date = EDTFDateString(required=True)
    subjects = fields.List(fields.Nested(SubjectSchemaV1))
    contributors = fields.List(fields.Nested(ContributorSchemaV1))
    dates = fields.List(fields.Nested(DateSchemaV1))
    language = ISOLangString()
    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifierSchemaV1))
    version = SanitizedUnicode()
    licenses = fields.List(fields.Nested(LicenseSchemaV1))
    descriptions = fields.List(fields.Nested(DescriptionSchemaV1))
    locations = fields.List(fields.Nested(LocationSchemaV1))
    references = fields.List(fields.Nested(ReferenceSchemaV1))

    _internal_notes = fields.List(fields.Nested(InternalNoteSchemaV1))

    # TODO (Alex): this might go in a separate top-level field?
    # extensions = fields.Method('dump_extensions', 'load_extensions')

    def dump_extensions(self, obj):
        """Dumps the extensions value.

        :params obj: invenio_records_files.api.Record instance
        """
        current_app_metadata_extensions = (
            current_app.extensions['invenio-rdm-records'].metadata_extensions
        )
        ExtensionSchema = current_app_metadata_extensions.to_schema()
        return ExtensionSchema().dump(obj.get('extensions', {}))

    def load_extensions(self, value):
        """Loads the 'extensions' field.

        :params value: content of the input's 'extensions' field
        """
        current_app_metadata_extensions = (
            current_app.extensions['invenio-rdm-records'].metadata_extensions
        )
        ExtensionSchema = current_app_metadata_extensions.to_schema()

        return ExtensionSchema().load(value)

    @post_load
    def post_load_publication_date(self, obj, **kwargs):
        """Add '_publication_date_search' field."""
        prepare_publication_date(obj)
        return obj
