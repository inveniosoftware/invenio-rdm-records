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
from invenio_communities.records.api import Record, RecordCommunitiesCollection
from invenio_records_rest.schemas import Nested
from invenio_records_rest.schemas.fields import DateString, GenMethod, \
    PersistentIdentifier, SanitizedUnicode
from invenio_rest.serializer import BaseSchema
from marshmallow import ValidationError, fields, post_load, validate, \
    validates, validates_schema
from marshmallow.schema import SchemaMeta

from ..vocabularies import Vocabularies
from .fields import EDTFLevel0DateString
from .utils import api_link_for, validate_iso639_3


def validate_entry(vocabulary_key, entry_key):
    """Validates if an entry is valid for a vocabulary.

    :param vocabulary_key: str, Vocabulary key
    :param entry_key: str, specific entry key

    raises marshmallow.ValidationError if entry is not valid.
    """
    vocabulary = Vocabularies.get_vocabulary(vocabulary_key)
    obj = vocabulary.get_entry_by_dict(entry_key)
    if not obj:
        raise ValidationError(vocabulary.get_invalid(entry_key))


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
    affiliations = fields.List(Nested(AffiliationSchemaV1))


class ContributorSchemaV1(CreatorSchemaV1):
    """Contributor schema."""

    role = SanitizedUnicode(required=True)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate role."""
        validate_entry('contributors.role', data)


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
        validate_entry('resource_type', data)


class TitleSchemaV1(BaseSchema):
    """Schema for the additional title."""

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    type = SanitizedUnicode(missing='MainTitle')
    lang = SanitizedUnicode(validate=validate_iso639_3)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate type."""
        validate_entry('titles.type', data)


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
    resource_type = Nested(ResourceTypeSchemaV1)


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

    point = Nested(PointSchemaV1)
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


class CommunitiesRequestV1(BaseSchema):
    """Community Request Schema."""

    id = SanitizedUnicode(required=True)
    comid = SanitizedUnicode(required=True)
    title = SanitizedUnicode(required=True)
    request_id = SanitizedUnicode()
    created_by = fields.Integer()
    links = fields.Method('get_links')

    def get_links(self, obj):
        """Get links."""
        res = {
            'self': api_link_for(
                'community_inclusion_request',
                id=obj['comid'], request_id=obj['request_id']),
            'community': api_link_for('community', id=obj['comid']),
        }
        for action in ('accept', 'reject', 'comment'):
            res[action] = api_link_for(
                'community_inclusion_request_action',
                id=obj['comid'], request_id=obj['request_id'], action=action)
        return res


class CommunityStatusV1(BaseSchema):
    """Status of a community request."""

    pending = fields.List(Nested(CommunitiesRequestV1))
    accepted = fields.List(Nested(CommunitiesRequestV1))
    rejected = fields.List(Nested(CommunitiesRequestV1))


class MetadataSchemaV1(BaseSchema):
    """Schema for the record metadata."""

    # Administrative fields
    _access = Nested(AccessSchemaV1, required=True)
    _owners = fields.List(fields.Integer, validate=validate.Length(min=1),
                          required=True)
    _created_by = fields.Integer(required=True)
    _default_preview = SanitizedUnicode()
    _files = fields.List(Nested(FilesSchemaV1, dump_only=True))
    _internal_notes = fields.List(Nested(InternalNoteSchemaV1))
    _embargo_date = DateString(data_key="embargo_date",
                               attribute="embargo_date")
    _communities = GenMethod('dump_communities')
    _contact = SanitizedUnicode(data_key="contact", attribute="contact")

    # Metadata fields
    access_right = SanitizedUnicode(required=True)
    identifiers = Identifiers()
    creators = fields.List(Nested(CreatorSchemaV1), required=True)
    titles = fields.List(Nested(TitleSchemaV1), required=True)
    resource_type = Nested(ResourceTypeSchemaV1, required=True)
    recid = PersistentIdentifier()
    publication_date = EDTFLevel0DateString(
        missing=lambda: date.today().isoformat()
    )
    subjects = fields.List(Nested(SubjectSchemaV1))
    contributors = fields.List(Nested(ContributorSchemaV1))
    dates = fields.List(Nested(DateSchemaV1))
    language = SanitizedUnicode(validate=validate_iso639_3)
    related_identifiers = fields.List(
        Nested(RelatedIdentifierSchemaV1))
    version = SanitizedUnicode()
    licenses = fields.List(Nested(LicenseSchemaV1))
    descriptions = fields.List(Nested(DescriptionSchemaV1))
    locations = fields.List(Nested(LocationSchemaV1))
    references = fields.List(Nested(ReferenceSchemaV1))
    extensions = fields.Method('dump_extensions', 'load_extensions')

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

    def dump_communities(self, obj):
        """Dumps communities related to the record."""
        # NOTE: If the field is already there, it's coming from ES
        if '_communities' in obj:
            return CommunityStatusV1().dump(obj['_communities'])

        record = self.context.get('record')
        if record:
            _record = Record(record, model=record.model)
            return CommunityStatusV1().dump(
                RecordCommunitiesCollection(_record).as_dict())

    @validates('_embargo_date')
    def validate_embargo_date(self, value):
        """Validate that embargo date is in the future."""
        if arrow.get(value).date() <= arrow.utcnow().date():
            raise ValidationError(
                _('Embargo date must be in the future.'),
                field_names=['embargo_date']
            )

    @validates('access_right')
    def validate_access_right(self, value):
        """Validate that access right is one of the allowed ones."""
        access_right_key = {'access_right': value}
        validate_entry('access_right', access_right_key)

    @post_load
    def post_load_publication_date(self, obj, **kwargs):
        """Add '_publication_date_search' field."""
        prepare_publication_date(obj)
        return obj


class RecordSchemaV1(BaseSchema):
    """Record schema."""

    # TODO: Use `RecordMetadataSchemaJSONV1` to inject PID in PUT/PATCH/...
    metadata = Nested(MetadataSchemaV1)
    bucket = fields.Str()
    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier(attribute='pid.pid_value')


def dump_empty(schema_or_field):
    """Return a full json-compatible dict with empty values.

    NOTE: This is only needed because the frontend needs it.
          This might change soon.
    """
    if isinstance(schema_or_field, (BaseSchema,)):
        schema = schema_or_field
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, SchemaMeta):
        # NOTE: Nested fields can pass a Schema class (SchemaMeta)
        #       or a Schema instance.
        #       Schema classes need to be instantiated to get .fields
        schema = schema_or_field()
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, fields.List):
        field = schema_or_field
        return [dump_empty(field.inner)]
    if isinstance(schema_or_field, Nested):
        field = schema_or_field
        return dump_empty(field.nested)

    return None
