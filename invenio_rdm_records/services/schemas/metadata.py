# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

import time
from urllib import parse

import arrow
import idutils
from edtf.parser.grammar import level0Expression
from flask import current_app
from flask_babelex import lazy_gettext as _
from marshmallow import INCLUDE, Schema, ValidationError, fields, post_load, \
    validate, validates, validates_schema
from marshmallow_utils.fields import EDTFDateString, GenFunction, \
    ISODateString, ISOLangString, LocalizedEDTFDateString, SanitizedUnicode

from .utils import validate_entry


def _no_duplicates(value_list):
    str_list = [str(value) for value in value_list]
    return len(value_list) == len(set(str_list))


class InternalNoteSchema(Schema):
    """Internal note shema."""

    user = SanitizedUnicode(required=True)
    note = SanitizedUnicode(required=True)
    timestamp = ISODateString(required=True)


class DateSchema(Schema):
    """Schema for date intervals."""

    DATE_TYPES = [
        "accepted",
        "available",
        "copyrighted",
        "collected",
        "created",
        "issued",
        "submitted",
        "updated",
        "valid",
        "withdrawn",
        "other"
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


class AffiliationSchema(Schema):
    """Affiliation of a creator/contributor."""

    name = SanitizedUnicode(required=True)
    identifiers = fields.Dict()

    @validates("identifiers")
    def validate_identifiers(self, value):
        """Validate well-formed identifiers are passed."""
        if len(value) == 0:
            raise ValidationError(_("Invalid identifier."))

        for identifier in value.keys():
            validator = getattr(idutils, 'is_' + identifier, None)
            # NOTE: identifier key cannot be empty string
            if not identifier or (validator and
                                  not validator(value.get(identifier))):
                raise ValidationError(_(f"Invalid identifier ({identifier})."))


class CreatorSchema(Schema):
    """Creator schema."""

    NAMES = [
        "organizational",
        "personal"
    ]

    # TODO: Need to revisit `name` in Deposit form:
    #       current mock-up doesn't have `name` field, so there is assumed
    #       work on the front-end to fill this value.
    name = SanitizedUnicode(required=True)
    type = SanitizedUnicode(validate=validate.OneOf(
                choices=NAMES,
                error=_(f'Invalid value. Choose one of {NAMES}.')
            ))
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = fields.Dict()
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    @validates("identifiers")
    def validate_identifiers(self, value):
        """Validate well-formed identifiers are passed."""
        schemes = ['orcid', 'ror']

        if any(scheme not in schemes for scheme in value.keys()):
            raise ValidationError(
                [_(f"Invalid value. Choose one of {schemes}.")]
            )

        if 'orcid' in value:
            if not idutils.is_orcid(value.get('orcid')):
                raise ValidationError({'orcid': [_("Invalid value.")]})

        if 'ror' in value:
            if not idutils.is_ror(value.get('ror')):
                raise ValidationError({'ror': [_("Invalid value.")]})

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate identifier based on type."""
        if data['type'] == "personal":
            person_identifiers = ['orcid']
            identifiers = data.get('identifiers', {}).keys()
            if any([i not in person_identifiers for i in identifiers]):
                messages = [
                    _(f"Invalid value. Choose one of {person_identifiers}.")
                ]
                raise ValidationError({"identifiers": messages})

        elif data['type'] == "organizational":
            org_identifiers = ['ror']
            identifiers = data.get('identifiers', {}).keys()
            if any([i not in org_identifiers for i in identifiers]):
                messages = [
                    _(f"Invalid value. Choose one of {org_identifiers}.")
                ]
                raise ValidationError({"identifiers": messages})


class ContributorSchema(CreatorSchema):
    """Contributor schema."""

    role = SanitizedUnicode(required=True)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate role."""
        validate_entry('contributors.role', data)


class ResourceTypeSchema(Schema):
    """Resource type schema."""

    type = fields.Str(required=True)
    subtype = fields.Str()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate resource type."""
        validate_entry('resource_type', data)


class TitleSchema(Schema):
    """Schema for the additional title."""

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    type = SanitizedUnicode()
    lang = ISOLangString()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate type."""
        if data.get('type'):
            validate_entry('titles.type', data)


class DescriptionSchema(Schema):
    """Schema for the additional descriptions."""

    DESCRIPTION_TYPES = [
          "abstract",
          "methods",
          "seriesinformation",
          "tableofcontents",
          "technicalinfo",
          "other"
    ]
    description = SanitizedUnicode(required=True,
                                   validate=validate.Length(min=3))
    type = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=DESCRIPTION_TYPES,
            error=_('Invalid description type. {input} not one of {choices}.')
        ))
    lang = ISOLangString()


def _is_uri(uri):
    try:
        parse.urlparse(uri)
        return True
    except AttributeError:
        return False


class RightsSchema(Schema):
    """License schema."""

    rights = SanitizedUnicode(required=True)
    uri = SanitizedUnicode(
        validate=_is_uri,
        error=_('Wrong URI format. Should follow RFC 3986.')
    )
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class SubjectSchema(Schema):
    """Subject schema."""

    subject = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()


class DateSchema(Schema):
    """Schema for date intervals."""

    DATE_TYPES = [
        "accepted",
        "available",
        "copyrighted",
        "collected",
        "created",
        "issued",
        "submitted",
        "updated",
        "valid",
        "withdrawn",
        "other"
    ]

    date = EDTFDateString(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(
            choices=DATE_TYPES,
            error=_('Invalid date type. {input} not one of {choices}.')
        ))
    description = fields.Str()


# 'Fake' Identifiers Field
def _not_blank(error_msg):
    """Returns a non-blank validation rule with custom error message."""
    return validate.Length(min=1, error=error_msg)


class IdentifierSchema(Schema):
    """Identifier schema.

    NOTE: Equivalent to DataCite's alternate identifier.
    """

    identifier = SanitizedUnicode(
        required=True, validate=_not_blank(_('Identifier cannot be blank.')))
    scheme = SanitizedUnicode(
        required=True, validate=_not_blank(_('Scheme cannot be blank.')))


class RelatedIdentifierSchema(Schema):
    """Related identifier schema."""

    RELATIONS = [
        "iscitedby",
        "cites",
        "issupplementto",
        "issupplementedby",
        "iscontinuedby",
        "continues",
        "isdescribedby",
        "describes",
        "hasmetadata",
        "ismetadatafor",
        "hasversion",
        "isversionof",
        "isnewversionof",
        "ispreviousversionof",
        "ispartof",
        "haspart",
        "isreferencedby",
        "references",
        "isdocumentedby",
        "documents",
        "iscompiledby",
        "compiles",
        "isvariantformof",
        "isoriginalformof",
        "isidenticalto",
        "isreviewedby",
        "reviews",
        "isderivedfrom",
        "issourceof",
        "isrequiredby",
        "requires",
        "isobsoletedby",
        "obsoletes"
    ]

    SCHEMES = [
        "ark",
        "arxiv",
        "bibcode",
        "doi",
        "ean13",
        "eissn",
        "handle",
        "igsn",
        "isbn",
        "issn",
        "istc",
        "lissn",
        "lsid",
        "pmid",
        "purl",
        "upc",
        "url",
        "urn",
        "w3id"
    ]

    identifier = SanitizedUnicode(
        required=True,
        validate=_not_blank(_('Identifier cannot be blank.'))
    )
    scheme = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=SCHEMES,
            error=_('Invalid related identifier scheme. ' +
                    '{input} not one of {choices}.')
        ))
    relation_type = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=RELATIONS,
            error=_('Invalid relation type. {input} not one of {choices}.')
        ))
    resource_type = fields.Nested(ResourceTypeSchema)


class ReferenceSchema(Schema):
    """Reference schema."""

    SCHEMES = [
        "isni",
        "grid",
        "crossreffunderid",
        "other"
    ]
    reference = SanitizedUnicode(required=True)
    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode(validate=validate.OneOf(
            choices=SCHEMES,
            error=_('Invalid reference scheme. {input} not one of {choices}.')
        ))


class PointSchema(Schema):
    """Point schema."""

    lat = fields.Number(required=True)
    lon = fields.Number(required=True)


class LocationSchema(Schema):
    """Location schema."""

    point = fields.Nested(PointSchema)
    place = SanitizedUnicode(required=True)
    description = SanitizedUnicode()


class MetadataSchema(Schema):
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
    resource_type = fields.Nested(ResourceTypeSchema, required=True)
    creators = fields.List(fields.Nested(CreatorSchema), required=True)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    additional_titles = fields.List(fields.Nested(TitleSchema))
    publisher = SanitizedUnicode()
    publication_date = EDTFDateString(required=True)
    subjects = fields.List(fields.Nested(SubjectSchema))
    contributors = fields.List(fields.Nested(ContributorSchema))
    dates = fields.List(fields.Nested(DateSchema))
    languages = fields.List(ISOLangString())
    # alternate identifiers
    identifiers = fields.List(fields.Nested(IdentifierSchema))
    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifierSchema),
        validate=_no_duplicates,
        error=_('Invalid related identifiers cannot contain duplicates.')
    )
    sizes = fields.List(SanitizedUnicode(
        validate=_not_blank(_('Size cannot be a blank string.'))))
    formats = fields.List(SanitizedUnicode(
        validate=_not_blank(_('Format cannot be a blank string.'))))
    version = SanitizedUnicode()
    rights = fields.List(fields.Nested(RightsSchema))
    description = SanitizedUnicode(validate=validate.Length(min=3))
    additional_descriptions = fields.List(fields.Nested(DescriptionSchema))
    # locations = fields.List(fields.Nested(LocationSchema))
    # funding
    # references = fields.List(fields.Nested(ReferenceSchema))

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
