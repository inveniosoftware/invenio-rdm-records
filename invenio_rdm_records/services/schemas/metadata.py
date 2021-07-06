# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from functools import partial
from urllib import parse

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, post_load, validate, \
    validates_schema
from marshmallow_utils.fields import EDTFDateString, IdentifierSet, \
    SanitizedHTML, SanitizedUnicode
from marshmallow_utils.schemas import GeometryObjectSchema, IdentifierSchema


def _not_blank(error_msg):
    """Returns a non-blank validation rule with custom error message."""
    return validate.Length(min=1, error=error_msg)


def _valid_url(error_msg):
    """Returns a URL validation rule with custom error message."""
    return validate.URL(error=error_msg)


class AffiliationSchema(Schema):
    """Affiliation of a creator/contributor.

    Cannot inherit VocabularySchema because id is optional.
    """

    id = SanitizedUnicode()
    name = SanitizedUnicode()

    @validates_schema
    def validate_affiliation(self, data, **kwargs):
        """Validates that either id either name are present."""
        only_one = bool(data.get("id")) ^ bool(data.get("name"))
        if not only_one:
            raise ValidationError(
                "Only existing affiliation id or a free text name can " +
                "be present",
                'affiliations'  # name of field to report error for
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
            # [] needed to mirror error message above
            "required": [_(f'Invalid value. Choose one of {NAMES}.')]
        }
    )
    name = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(partial(
            IdentifierSchema,
            # It is intended to allow org schemes to be sent as personal
            # and viceversa. This is a trade off learnt from running
            # Zenodo in production.
            allowed_schemes=["orcid", "isni", "gnd", "ror"]
        ))
    )

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names based on type."""
        if data['type'] == "personal":
            if not data.get('family_name'):
                messages = [_("Family name must be filled.")]
                raise ValidationError({
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


class VocabularySchema(Schema):
    """Invenio Vocabulary schema."""

    id = SanitizedUnicode(required=True)
    title = fields.Dict(dump_only=True)


class CreatorSchema(Schema):
    """Creator schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)
    role = fields.Nested(VocabularySchema)
    affiliations = fields.List(fields.Nested(AffiliationSchema))


class ContributorSchema(Schema):
    """Contributor schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)
    role = fields.Nested(VocabularySchema, required=True)
    affiliations = fields.List(fields.Nested(AffiliationSchema))


class TitleSchema(Schema):
    """Schema for the additional title."""

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    type = fields.Nested(VocabularySchema, required=True)
    lang = fields.Nested(VocabularySchema)


class DescriptionSchema(Schema):
    """Schema for the additional descriptions."""

    description = SanitizedHTML(required=True,
                                validate=validate.Length(min=3))
    type = fields.Nested(VocabularySchema, required=True)
    lang = fields.Nested(VocabularySchema)


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
        super().__init__(
            fail_on_unknown=False, identifier_required=False, **kwargs)

    id = SanitizedUnicode()
    title = SanitizedUnicode()
    description = SanitizedUnicode()
    link = SanitizedUnicode(
        validate=_valid_url(_('Not a valid URL.'))
    )


class DateSchema(Schema):
    """Schema for date intervals."""

    date = EDTFDateString(required=True)
    type = fields.Nested(VocabularySchema, required=True)
    description = fields.Str()


class RelatedIdentifierSchema(IdentifierSchema):
    """Related identifier schema."""

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

    relation_type = fields.Nested(VocabularySchema, required=True)
    resource_type = fields.Nested(VocabularySchema)


class FunderSchema(IdentifierSchema):
    """Funder schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            fail_on_unknown=False, identifier_required=False, **kwargs)

    name = SanitizedUnicode(
        required=True,
        validate=_not_blank(_('Name cannot be blank.'))
    )


class AwardSchema(IdentifierSchema):
    """Award schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            fail_on_unknown=False, identifier_required=False, **kwargs)

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
                         identifier_required=False, **kwargs)

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
        fields.Nested(partial(IdentifierSchema, fail_on_unknown=False)),
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


class FeatureSchema(Schema):
    """Location feature schema."""

    features = fields.List(fields.Nested(LocationSchema))


class MetadataSchema(Schema):
    """Schema for the record metadata."""

    field_load_permissions = {
        # TODO: define "can_admin" action
    }

    field_dump_permissions = {
        # TODO: define "can_admin" action
    }

    # Metadata fields
    resource_type = fields.Nested(VocabularySchema, required=True)
    creators = fields.List(
        fields.Nested(CreatorSchema),
        required=True,
        validate=validate.Length(
            min=1, error=_("Missing data for required field.")
        )
    )
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    additional_titles = fields.List(fields.Nested(TitleSchema))
    publisher = SanitizedUnicode()
    publication_date = EDTFDateString(required=True)
    subjects = fields.List(fields.Nested(VocabularySchema))
    contributors = fields.List(fields.Nested(ContributorSchema))
    dates = fields.List(fields.Nested(DateSchema))
    languages = fields.List(fields.Nested(VocabularySchema))
    # alternate identifiers
    identifiers = IdentifierSet(
        fields.Nested(partial(IdentifierSchema, fail_on_unknown=False))
    )
    related_identifiers = fields.List(fields.Nested(RelatedIdentifierSchema))
    sizes = fields.List(SanitizedUnicode(
        validate=_not_blank(_('Size cannot be a blank string.'))))
    formats = fields.List(SanitizedUnicode(
        validate=_not_blank(_('Format cannot be a blank string.'))))
    version = SanitizedUnicode()
    rights = fields.List(fields.Nested(RightsSchema))
    description = SanitizedHTML(validate=validate.Length(min=3))
    additional_descriptions = fields.List(fields.Nested(DescriptionSchema))
    locations = fields.Nested(FeatureSchema)
    funding = fields.List(fields.Nested(FundingSchema))
    references = fields.List(fields.Nested(ReferenceSchema))
