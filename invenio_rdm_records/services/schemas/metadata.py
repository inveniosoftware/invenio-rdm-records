# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from functools import partial
from urllib import parse

from flask_babelex import lazy_gettext as _
from marshmallow import EXCLUDE, INCLUDE, Schema, ValidationError, fields, \
    post_load, validate, validates_schema
from marshmallow_utils.fields import EDTFDateString, IdentifierSet, \
    ISOLangString, SanitizedUnicode
from marshmallow_utils.schemas import GeometryObjectSchema, IdentifierSchema

from .utils import validate_entry


def _not_blank(error_msg):
    """Returns a non-blank validation rule with custom error message."""
    return validate.Length(min=1, error=error_msg)


class AffiliationSchema(Schema):
    """Affiliation of a creator/contributor."""

    name = SanitizedUnicode(required=True)
    identifiers = IdentifierSet(
        fields.Nested(partial(IdentifierSchema, allow_all=True)),
    )


class PersonOrOrganizationSchema(Schema):
    """Person or Organization schema."""

    NAMES = [
        "organizational",
        "personal"
    ]

    type = SanitizedUnicode(
        required=True,
        validate=validate.OneOf(
            choices=NAMES,
            error=_(f'Invalid value. Choose one of {NAMES}.')
        ),
        error_messages={
            # NOTE: [] needed to mirror above error message
            "required": [_(f'Invalid value. Choose one of {NAMES}.')]
        }
    )
    name = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(partial(
            IdentifierSchema,
            # It is intendedly allowing org schemes to be sent as personal
            # and viceversa. This is a trade off learnt from running
            # Zenodo in production.
            allowed_schemes=["orcid", "isni", "gnd", "ror"]
        ))
    )

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names based on type."""
        if data['type'] == "personal":
            if not (data.get('given_name') or data.get('family_name')):
                messages = [_("Family name or given name must be filled.")]
                raise ValidationError({
                    "given_name": messages,
                    "family_name": messages
                })

        elif data['type'] == "organizational":
            if not data.get('name'):
                messages = [_('Name cannot be blank.')]
                raise ValidationError({"name": messages})

    @post_load
    def update_names(self, data, **kwargs):
        """Update names for organization / person.

        Fill name from given_name and family_name if person.
        Remove given_name and family_name if organization.
        """
        if data["type"] == "personal":
            names = [data.get("family_name"), data.get("given_name")]
            data["name"] = ", ".join([n for n in names if n])

        elif data['type'] == "organizational":
            if 'family_name' in data:
                del data['family_name']
            if 'given_name' in data:
                del data['given_name']

        return data


class CreatorSchema(Schema):
    """Creator schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)
    role = SanitizedUnicode()
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    @validates_schema
    def validate_role(self, data, **kwargs):
        """Validate role."""
        if 'role' in data:
            validate_entry('creators.role', data)


class ContributorSchema(Schema):
    """Contributor schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema)
    role = SanitizedUnicode(required=True)
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    @validates_schema
    def validate_role(self, data, **kwargs):
        """Validate role."""
        validate_entry('contributors.role', data)


class ResourceType(fields.Field):
    """Represents a Resource type as a field.

    This is needed to get a nice error message directly under the
    'resource_type' key. Otherwise the error message is under the "_schema"
    key.
    """

    class ResourceTypeSchema(Schema):
        """Resource type schema."""

        type = fields.Str(required=True)
        subtype = fields.Str()

        @validates_schema
        def validate_data(self, data, **kwargs):
            """Validate resource type."""
            validate_entry('resource_type', data)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return ResourceType.ResourceTypeSchema().load(value)
        except ValidationError as error:
            error_content = (
                []
                + error.messages.get("type", [])
                + error.messages.get("subtype", [])
                + error.messages.get("_schema", [])
            )

            raise ValidationError(error_content)


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


class RightsSchema(IdentifierSchema):
    """License schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allow_all=True, required=False, **kwargs)

    id = SanitizedUnicode()
    title = SanitizedUnicode()
    description = SanitizedUnicode()
    link = SanitizedUnicode(
        validate=_is_uri,
        error=_('Wrong URI format. Should follow RFC 3986.')
    )


class SubjectSchema(IdentifierSchema):
    """Subject schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allow_all=True, required=False, **kwargs)

    subject = SanitizedUnicode(required=True)


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


class RelatedIdentifierSchema(IdentifierSchema):
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

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allowed_schemes=self.SCHEMES, **kwargs)

    relation_type = SanitizedUnicode(required=True, validate=validate.OneOf(
            choices=RELATIONS,
            error=_('Invalid relation type. {input} not one of {choices}.')
        ))
    resource_type = ResourceType()


class FunderSchema(IdentifierSchema):
    """Funder schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allow_all=True, required=False, **kwargs)

    name = SanitizedUnicode(
        required=True,
        validate=_not_blank(_('Name cannot be blank.'))
    )


class AwardSchema(IdentifierSchema):
    """Award schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allow_all=True, required=False, **kwargs)

    title = SanitizedUnicode(
        required=True,
        validate=_not_blank(_('Name cannot be blank.'))
    )
    number = SanitizedUnicode(
        required=True,
        validate=_not_blank(_('Name cannot be blank.'))
    )


class FundingSchema(Schema):
    """Funding schema."""

    funder = fields.Nested(FunderSchema)
    award = fields.Nested(AwardSchema)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate either funder or award is present."""
        funder = data.get('funder')
        award = data.get('award')
        if not funder and not award:
            raise ValidationError(
                {"funding": _("At least award or funder shold be present.")})


class ReferenceSchema(IdentifierSchema):
    """Reference schema."""

    SCHEMES = [
        "isni",
        "grid",
        "crossreffunderid",
        "other"
    ]

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allowed_schemes=self.SCHEMES,
                         required=False, **kwargs)

    reference = SanitizedUnicode(required=True)


class PointSchema(Schema):
    """Point schema."""

    lat = fields.Number(required=True)
    lon = fields.Number(required=True)


class LocationSchema(Schema):
    """Location schema."""

    geometry = fields.Nested(GeometryObjectSchema)
    place = SanitizedUnicode()
    identifiers = fields.List(
        fields.Nested(partial(IdentifierSchema, allow_all=True)),
    )
    description = SanitizedUnicode()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate identifier based on type."""
        if not data.get('geometry') and not data.get('place') and \
           not data.get('identifiers') and not data.get('description'):
            raise ValidationError({
                "locations": _("At least one of ['geometry', 'place', \
                'identifiers', 'description'] shold be present.")
            })


class LanguageSchema(Schema):
    """Language schema."""

    class Meta:
        """Meta class to discard unknown fields."""

        unknown = EXCLUDE

    id = SanitizedUnicode(required=True)
    title = fields.Raw(attribute="metadata.title", dump_only=True)
    description = fields.Raw(
        attribute="metadata.description", dump_only=True)


class MetadataSchema(Schema):
    """Schema for the record metadata."""

    field_load_permissions = {
        # TODO: define "can_admin" action
    }

    field_dump_permissions = {
        # TODO: define "can_admin" action
    }

    class Meta:
        """Meta class to accept unknwon fields."""

        unknown = INCLUDE

    # Metadata fields
    resource_type = ResourceType(required=True)
    creators = fields.List(fields.Nested(CreatorSchema), required=True)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    additional_titles = fields.List(fields.Nested(TitleSchema))
    publisher = SanitizedUnicode()
    publication_date = EDTFDateString(required=True)
    subjects = fields.List(fields.Nested(SubjectSchema))
    contributors = fields.List(fields.Nested(ContributorSchema))
    dates = fields.List(fields.Nested(DateSchema))
    languages = fields.List(fields.Nested(LanguageSchema))
    # alternate identifiers
    identifiers = IdentifierSet(
        fields.Nested(partial(IdentifierSchema, allow_all=True))
    )
    related_identifiers = fields.List(fields.Nested(RelatedIdentifierSchema))
    sizes = fields.List(SanitizedUnicode(
        validate=_not_blank(_('Size cannot be a blank string.'))))
    formats = fields.List(SanitizedUnicode(
        validate=_not_blank(_('Format cannot be a blank string.'))))
    version = SanitizedUnicode()
    rights = fields.List(fields.Nested(RightsSchema))
    description = SanitizedUnicode(validate=validate.Length(min=3))
    additional_descriptions = fields.List(fields.Nested(DescriptionSchema))
    locations = fields.List(fields.Nested(LocationSchema))
    funding = fields.List(fields.Nested(FundingSchema))
    references = fields.List(fields.Nested(ReferenceSchema))
