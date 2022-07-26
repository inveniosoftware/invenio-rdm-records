# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from functools import partial
from urllib import parse

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_vocabularies.contrib.affiliations.schema import AffiliationRelationSchema
from invenio_vocabularies.contrib.awards.schema import AwardRelationSchema
from invenio_vocabularies.contrib.funders.schema import FunderRelationSchema
from invenio_vocabularies.contrib.subjects.schema import SubjectRelationSchema
from invenio_vocabularies.services.schema import (
    VocabularyRelationSchema as VocabularySchema,
)
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    validate,
    validates,
    validates_schema,
)
from marshmallow_utils.fields import (
    EDTFDateString,
    IdentifierSet,
    SanitizedHTML,
    SanitizedUnicode,
)
from marshmallow_utils.schemas import GeometryObjectSchema, IdentifierSchema
from werkzeug.local import LocalProxy

record_personorg_schemes = LocalProxy(
    lambda: current_app.config["RDM_RECORDS_PERSONORG_SCHEMES"]
)


record_identifiers_schemes = LocalProxy(
    lambda: current_app.config["RDM_RECORDS_IDENTIFIERS_SCHEMES"]
)


record_references_schemes = LocalProxy(
    lambda: current_app.config["RDM_RECORDS_REFERENCES_SCHEMES"]
)


record_location_schemes = LocalProxy(
    lambda: current_app.config["RDM_RECORDS_LOCATION_SCHEMES"]
)


def _not_blank(error_msg):
    """Returns a non-blank validation rule with custom error message."""
    return validate.Length(min=1, error=error_msg)


def _valid_url(error_msg):
    """Returns a URL validation rule with custom error message."""
    return validate.URL(error=error_msg)


def locale_validation(value, field_name):
    """Validates the locale value."""
    valid_locales = current_app.extensions["invenio-i18n"].get_locales()
    valid_locales_code = [v.language for v in valid_locales]
    if value:
        if len(value.keys()) > 1:
            raise ValidationError(_("Only one value is accepted."), field_name)
        elif list(value.keys())[0] not in valid_locales_code:
            raise ValidationError(_("Not a valid locale."), field_name)


class PersonOrOrganizationSchema(Schema):
    """Person or Organization schema."""

    NAMES = ["organizational", "personal"]

    type = SanitizedUnicode(
        required=True,
        validate=validate.OneOf(
            choices=NAMES,
            error=_("Invalid value. Choose one of {NAMES}.").format(NAMES=NAMES),
        ),
        error_messages={
            # [] needed to mirror error message above
            "required": [_("Invalid value. Choose one of {NAMES}.").format(NAMES=NAMES)]
        },
    )
    name = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                # It is intended to allow org schemes to be sent as personal
                # and viceversa. This is a trade off learnt from running
                # Zenodo in production.
                allowed_schemes=record_personorg_schemes,
            )
        )
    )

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names based on type."""
        if data["type"] == "personal":
            if not data.get("family_name"):
                messages = [_("Family name cannot be blank.")]
                raise ValidationError({"family_name": messages})

        elif data["type"] == "organizational":
            if not data.get("name"):
                messages = [_("Name cannot be blank.")]
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

        elif data["type"] == "organizational":
            if "family_name" in data:
                del data["family_name"]
            if "given_name" in data:
                del data["given_name"]

        return data


class CreatorSchema(Schema):
    """Creator schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)
    role = fields.Nested(VocabularySchema)
    affiliations = fields.List(fields.Nested(AffiliationRelationSchema))


class ContributorSchema(Schema):
    """Contributor schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)
    role = fields.Nested(VocabularySchema, required=True)
    affiliations = fields.List(fields.Nested(AffiliationRelationSchema))


class TitleSchema(Schema):
    """Schema for the additional title."""

    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    type = fields.Nested(VocabularySchema, required=True)
    lang = fields.Nested(VocabularySchema)


class DescriptionSchema(Schema):
    """Schema for the additional descriptions."""

    description = SanitizedHTML(required=True, validate=validate.Length(min=3))
    type = fields.Nested(VocabularySchema, required=True)
    lang = fields.Nested(VocabularySchema)


def _is_uri(uri):
    try:
        parse.urlparse(uri)
        return True
    except AttributeError:
        return False


class PropsSchema(Schema):
    """Schema for the URL schema."""

    url = SanitizedUnicode(validate=_valid_url(_("Not a valid URL.")))
    scheme = SanitizedUnicode()


class RightsSchema(Schema):
    """License schema."""

    id = SanitizedUnicode()
    title = fields.Dict()
    description = fields.Dict()
    icon = fields.Str(dump_only=True)
    props = fields.Nested(PropsSchema)
    link = SanitizedUnicode(validate=_valid_url(_("Not a valid URL.")))

    @validates("title")
    def validate_title(self, value):
        """Validates that title contains only one valid locale."""
        locale_validation(value, "title")

    @validates("description")
    def validate_description(self, value):
        """Validates that description contains only one valid locale."""
        locale_validation(value, "description")

    @validates_schema
    def validate_rights(self, data, **kwargs):
        """Validates that id xor name are present."""
        id_ = data.get("id")
        title = data.get("title")

        if not id_ and not title:
            raise ValidationError(
                _("An existing id or a free text title must be present"), "rights"
            )
        elif id_ and len(data.values()) > 1:
            raise ValidationError(
                _(
                    "Only an existing id or free text title/description/link"
                    + " is accepted, but not both cases at the same time"
                ),
                "rights",
            )


class DateSchema(Schema):
    """Schema for date intervals."""

    date = EDTFDateString(required=True)
    type = fields.Nested(VocabularySchema, required=True)
    description = fields.Str()


class RelatedIdentifierSchema(IdentifierSchema):
    """Related identifier schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(allowed_schemes=record_identifiers_schemes, **kwargs)

    relation_type = fields.Nested(VocabularySchema)
    resource_type = fields.Nested(VocabularySchema)

    @validates_schema
    def validate_related_identifier(self, data, **kwargs):
        """Validate the related identifiers."""
        relation_type = data.get("relation_type")
        errors = dict()

        if not relation_type:
            errors["relation_type"] = self.error_messages["required"]

        if errors:
            raise ValidationError(errors)


class FundingSchema(Schema):
    """Funding schema."""

    funder = fields.Nested(FunderRelationSchema, required=True)
    award = fields.Nested(AwardRelationSchema)


class ReferenceSchema(IdentifierSchema):
    """Reference schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            allowed_schemes=record_references_schemes,
            identifier_required=False,
            **kwargs
        )

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
        fields.Nested(
            partial(IdentifierSchema, allowed_schemes=record_location_schemes)
        )
    )
    description = SanitizedUnicode()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate identifier based on type."""
        if (
            not data.get("geometry")
            and not data.get("place")
            and not data.get("identifiers")
            and not data.get("description")
        ):
            raise ValidationError(
                {
                    "locations": _(
                        "At least one of ['geometry', 'place', \
                identifiers', 'description'] must be present."
                    )
                }
            )


class FeatureSchema(Schema):
    """Location feature schema."""

    features = fields.List(fields.Nested(LocationSchema))


class MetadataSchema(Schema):
    """Schema for the record metadata."""

    # Metadata fields
    resource_type = fields.Nested(VocabularySchema, required=True)
    creators = fields.List(
        fields.Nested(CreatorSchema),
        required=True,
        validate=validate.Length(min=1, error=_("Missing data for required field.")),
    )
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    additional_titles = fields.List(fields.Nested(TitleSchema))
    publisher = SanitizedUnicode()
    publication_date = EDTFDateString(required=True)
    subjects = fields.List(fields.Nested(SubjectRelationSchema))
    contributors = fields.List(fields.Nested(ContributorSchema))
    dates = fields.List(fields.Nested(DateSchema))
    languages = fields.List(fields.Nested(VocabularySchema))
    # alternate identifiers
    identifiers = IdentifierSet(
        fields.Nested(
            partial(IdentifierSchema, allowed_schemes=record_identifiers_schemes)
        )
    )
    related_identifiers = fields.List(fields.Nested(RelatedIdentifierSchema))
    sizes = fields.List(
        SanitizedUnicode(validate=_not_blank(_("Size cannot be a blank string.")))
    )
    formats = fields.List(
        SanitizedUnicode(validate=_not_blank(_("Format cannot be a blank string.")))
    )
    version = SanitizedUnicode()
    rights = fields.List(fields.Nested(RightsSchema))
    description = SanitizedHTML(validate=validate.Length(min=3))
    additional_descriptions = fields.List(fields.Nested(DescriptionSchema))
    locations = fields.Nested(FeatureSchema)
    funding = fields.List(fields.Nested(FundingSchema))
    references = fields.List(fields.Nested(ReferenceSchema))
