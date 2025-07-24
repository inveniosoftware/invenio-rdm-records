# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021-2025 Graz University of Technology.
# Copyright (C) 2022-2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from copy import deepcopy
from functools import partial

from babel_edtf import parse_edtf
from edtf.parser.grammar import ParseException
from flask import current_app, g
from flask_resources import BaseObjectSchema
from invenio_communities.communities.resources.ui_schema import (
    _community_permission_check,
)
from invenio_i18n import get_locale
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import CustomFieldsSchemaUI
from invenio_vocabularies.contrib.awards.serializer import AwardL10NItemSchema
from invenio_vocabularies.contrib.funders.serializer import FunderL10NItemSchema
from invenio_vocabularies.resources import L10NString, VocabularyL10Schema
from marshmallow import Schema, fields, missing, post_dump, pre_dump
from marshmallow_utils.fields import FormatDate as FormatDate_
from marshmallow_utils.fields import FormatEDTF as FormatEDTF_
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode, StrippedHTML
from marshmallow_utils.fields.babel import gettext_from_dict
from pyparsing import ParseException

from ....services.request_policies import RDMRecordDeletionPolicy
from ....services.schemas.fields import SanitizedHTML
from .fields import AccessStatusField


def current_default_locale():
    """Get the Flask app's default locale."""
    if current_app:
        return current_app.config.get("BABEL_DEFAULT_LOCALE", "en")
    # Use english by default if not specified
    return "en"


# Partial to make short definitions in below schema.
FormatEDTF = partial(FormatEDTF_, locale=get_locale)
FormatDate = partial(FormatDate_, locale=get_locale)


def make_affiliation_index(attr, obj, *args):
    """Serializes creators/contributors for easier UI consumption.

    args takes 'object_key' and 'object_schema_cls'. it seems useless since it
    is not used, but the tests would fail. it could be that this is because of
    changes to fix RemovedInMarshmallow4Warning
    """
    # Copy so we don't modify in place the existing dict.
    creators = deepcopy(obj.get("metadata", {}).get(attr))
    if not creators:
        return missing

    affiliations_idx = {}
    # Below is a trick to make sure we can increment in the index inside
    # the apply_idx function without overwriting the outer scope.
    index = {"val": 1}
    affiliation_list = []

    def apply_idx(affiliation):
        """Map an affiliation into list of (index, affiliation string)."""
        name = affiliation.get("name")
        id_value = affiliation.get("id")
        if name not in affiliations_idx:
            affiliations_idx[name] = index["val"]
            affiliation_list.append([index["val"], name, id_value])
            index["val"] += 1
        idx = affiliations_idx[name]
        return [idx, name]

    # For each creator, apply the
    for creator in creators:
        if "affiliations" in creator:
            creator["affiliations"] = list(map(apply_idx, creator["affiliations"]))
        if "role" in creator:
            if "title" in creator["role"]:
                creator["role"]["title"] = gettext_from_dict(
                    creator["role"]["title"], get_locale(), current_default_locale()
                )

    return {
        attr: creators,
        "affiliations": affiliation_list,
    }


def record_version(obj):
    """Return record's version."""
    field_data = obj.get("metadata", {}).get("version")

    if not field_data:
        return f"v{obj['versions']['index']}"

    return field_data


def get_coordinates(obj):
    """Coordinates determined by geometry type."""
    geometry_type = obj.get("type", None)

    if geometry_type == "Point":
        return obj.get("coordinates", [])
    elif geometry_type == "Polygon":
        return obj.get("coordinates", [[[]]])
    else:
        return None


class RelatedIdentifiersSchema(Schema):
    """Localization of language titles."""

    identifier = fields.String()
    relation_type = fields.Nested(VocabularyL10Schema, attribute="relation_type")
    scheme = fields.String()
    resource_type = fields.Nested(VocabularyL10Schema, attribute="resource_type")


class AdditionalTitlesSchema(Schema):
    """Additional titles schema."""

    title = fields.String()
    type = fields.Nested(VocabularyL10Schema, attribute="type")
    lang = fields.Nested(VocabularyL10Schema, attribute="lang")


class AdditionalDescriptionsSchema(Schema):
    """Localization of additional descriptions."""

    description = SanitizedHTML(attribute="description")
    type = fields.Nested(VocabularyL10Schema, attribute="type")
    lang = fields.Nested(VocabularyL10Schema, attribute="lang")


class DatesSchema(Schema):
    """Localization of dates."""

    date = fields.String()
    type = fields.Nested(VocabularyL10Schema, attribute="type")
    description = StrippedHTML(attribute="description")


class RightsSchema(VocabularyL10Schema):
    """Rights schema."""

    description = L10NString(data_key="description_l10n")
    icon = fields.Str(dump_only=True)
    link = fields.String()
    props = fields.Dict()


class FundingSchema(Schema):
    """Schema for dumping funding in the UI."""

    award = fields.Nested(AwardL10NItemSchema)
    funder = fields.Nested(FunderL10NItemSchema)


class GeometrySchema(Schema):
    """Schema for geometry in the UI."""

    type = fields.Str()
    coordinates = fields.Function(get_coordinates)


class IdentifierSchema(Schema):
    """Schema for dumping identifier in the UI."""

    scheme = fields.Str()
    identifier = fields.Str()


class FeatureSchema(Schema):
    """Schema for dumping locations in the UI."""

    place = SanitizedUnicode()
    description = SanitizedUnicode()
    geometry = fields.Nested(GeometrySchema)
    identifiers = fields.List(fields.Nested(IdentifierSchema))


class LocationSchema(Schema):
    """Schema for dumping locations in the UI."""

    features = fields.List(fields.Nested(FeatureSchema))


class MeetingSchema(Schema):
    """Schema for dumping 'meeting' custom field in the UI."""

    acronym = SanitizedUnicode()
    dates = SanitizedUnicode()
    place = SanitizedUnicode()
    session_part = SanitizedUnicode()
    session = SanitizedUnicode()
    title = SanitizedUnicode()
    url = SanitizedUnicode()


def compute_publishing_information(obj):
    """Computes 'publishing information' string from custom fields."""

    def _format_journal(journal, publication_date):
        """Formats a journal object into a string based on its attributes.

        Example:
            _format_journal({"title": "The Effects of Climate Change", "volume": 10, "issue": 2, "pages": "15-22", "issn": "1234-5678", "publication_date": "2023-03-02})
            >>> 'The Effects of Climate Change, 10(2), 15-22, ISSN:1234-5678, 2023.'
        """
        journal_title = journal.get("title")
        journal_issn = journal.get("issn")
        journal_issue = journal.get("issue")
        journal_volume = journal.get("volume")
        journal_pages = journal.get("pages")

        try:
            publication_date_edtf = (
                parse_edtf(publication_date).lower_strict()
                if publication_date
                else None
            )
            publication_date_formatted = (
                f"{publication_date_edtf.tm_year}" if publication_date_edtf else None
            )
        except ParseException:
            publication_date_formatted = None

        title = f"{journal_title}" if journal_title else None
        vol_issue = f"{journal_volume}" if journal_volume else None

        if journal_issue:
            if vol_issue:
                vol_issue += f"({journal_issue})"
            else:
                vol_issue = f"{journal_issue}"
        pages = f"{journal_pages}" if journal_pages else None
        issn = f"ISSN: {journal_issn}" if journal_issn else None
        fields = [title, vol_issue, pages, issn, publication_date_formatted]

        formatted = ", ".join(filter(None, fields))
        formatted += "."

        return formatted if formatted else ""

    def _format_imprint(imprint, publisher):
        """Formats a imprint object into a string based on its attributes."""
        imprint_title = imprint.get("title")
        imprint_place = imprint.get("place")
        imprint_isbn = imprint.get("isbn")
        imprint_pages = imprint.get("pages")
        edition = imprint.get("edition")
        ed_form = f" {edition} ed." if edition else ""
        title_page = f"{imprint_title}{ed_form}" if imprint_title else None
        if imprint_pages:
            if title_page:
                title_page += f", {imprint_pages}."
            else:
                title_page = f"{imprint_pages}."
        elif title_page:
            title_page += "."
        else:
            title_page = None
        place = f"{imprint_place}." if imprint_place else None
        isbn = f"ISBN: {imprint_isbn}." if imprint_isbn else None
        formatted = " ".join(filter(None, [title_page, place, isbn]))

        return formatted

    def _format_thesis(thesis):
        """Formats a thesis entry into a string based on its attributes."""
        if not isinstance(thesis, dict):
            return thesis
        university = thesis.get("university")
        department = thesis.get("department")
        if university and department:
            university = f"{university} ({department})"
        elif university is None:
            university = department

        date_submitted = thesis.get("date_submitted")
        submitted = f"{_('Submitted: ')}{date_submitted}" if date_submitted else None
        date_defended = thesis.get("date_defended")
        defended = f"{_('Defended: ')}{date_defended}" if date_defended else None

        fields = [university, thesis.get("type"), submitted, defended]
        return ", ".join(filter(None, fields))

    attr = "custom_fields"
    field = obj.get(attr, {})
    publisher = obj.get("metadata", {}).get("publisher")

    # Retrieve publishing related custom fields
    journal = field.get("journal:journal")
    imprint = field.get("imprint:imprint")
    # "thesis:university" is deprecated and kept for compatibility, will be removed later.
    thesis = field.get("thesis:thesis") or field.get("thesis:university")

    publication_date = obj.get("metadata", {}).get("publication_date", None)
    result = {}
    if journal:
        journal_string = _format_journal(journal, publication_date)
        if journal_string:
            result.update({"journal": journal_string})

    if imprint and publisher:
        imprint_string = _format_imprint(imprint, publisher)
        result.update({"imprint": imprint_string})

    if thesis:
        thesis_string = _format_thesis(thesis)
        result.update({"thesis": thesis_string})

    if len(result.keys()) == 0:
        return missing

    return result


class TombstoneSchema(Schema):
    """Schema for a record tombstone."""

    removal_reason = fields.Nested(VocabularyL10Schema, attribute="removal_reason")

    note = fields.String(attribute="note")

    # This information is masked into a string in UIRecordSchema
    removed_by = fields.Raw(attribute="removed_by")

    removal_date_l10n_medium = FormatEDTF(attribute="removal_date", format="medium")

    removal_date_l10n_long = FormatEDTF(attribute="removal_date", format="long")

    citation_text = fields.String(attribute="citation_text")

    is_visible = fields.Boolean(attribute="is_visible")

    deletion_policy = fields.Method("get_policy_description")

    def get_policy_description(self, obj):
        """Get deletion policy description."""
        policy_id = obj.get("deletion_policy", {}).get("id", None)
        return RDMRecordDeletionPolicy.get_policy_description(policy_id)


class UIRecordSchema(BaseObjectSchema):
    """Schema for dumping extra information for the UI."""

    object_key = "ui"

    publication_date_l10n_medium = FormatEDTF(
        attribute="metadata.publication_date", format="medium"
    )

    publication_date_l10n_long = FormatEDTF(
        attribute="metadata.publication_date", format="long"
    )

    created_date_l10n_long = FormatDate(attribute="created", format="long")

    updated_date_l10n_long = FormatDate(attribute="updated", format="long")

    resource_type = fields.Nested(
        VocabularyL10Schema, attribute="metadata.resource_type"
    )

    additional_titles = fields.List(
        fields.Nested(AdditionalTitlesSchema), attribute="metadata.additional_titles"
    )

    # Custom fields
    custom_fields = fields.Nested(
        partial(CustomFieldsSchemaUI, fields_var="RDM_CUSTOM_FIELDS")
    )

    publishing_information = fields.Function(compute_publishing_information)

    conference = fields.Nested(MeetingSchema, attribute="custom_fields.meeting:meeting")

    access_status = AccessStatusField(attribute="access")

    creators = fields.Function(partial(make_affiliation_index, "creators"))

    contributors = fields.Function(partial(make_affiliation_index, "contributors"))

    languages = fields.List(
        fields.Nested(VocabularyL10Schema),
        attribute="metadata.languages",
    )

    description_stripped = StrippedHTML(attribute="metadata.description")

    version = fields.Function(record_version)

    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifiersSchema()),
        attribute="metadata.related_identifiers",
    )

    additional_descriptions = fields.List(
        fields.Nested(AdditionalDescriptionsSchema()),
        attribute="metadata.additional_descriptions",
    )

    dates = fields.List(fields.Nested(DatesSchema()), attribute="metadata.dates")

    rights = fields.List(fields.Nested(RightsSchema()), attribute="metadata.rights")

    is_draft = fields.Boolean(attribute="is_draft")

    funding = fields.List(
        fields.Nested(FundingSchema()),
        attribute="metadata.funding",
    )

    tombstone = fields.Nested(TombstoneSchema, attribute="tombstone")

    locations = fields.Nested(LocationSchema, attribute="metadata.locations")

    @post_dump(pass_original=True)
    def mask_removed_by(self, obj, orig, **kwargs):
        """Mask information about who removed the record."""
        if not (tombstone := obj.get("tombstone", None)):
            return obj

        masked = _("NA")
        removed_by = tombstone.get("removed_by", {}).get("user", None)
        orig_owner = orig["parent"]["access"]["owned_by"].get("user", None)

        if removed_by == "system":
            masked = _("System (automatic)")
        elif removed_by == orig_owner:
            masked = _("Owner")
        elif removed_by is not None:
            masked = _("Admin")

        obj["tombstone"]["removed_by"] = masked
        return obj

    @pre_dump
    def add_communities_permissions_and_roles(self, obj, **kwargs):
        """Inject current user's permission to community receiver."""
        receiver = (
            obj.get("expanded", {}).get("parent", {}).get("review", {}).get("receiver")
        )
        if receiver:
            can_include_directly = _community_permission_check(
                "include_directly", community=receiver, identity=g.identity
            )

            # use `ui` key to indicate that the extra information is injected only on
            # UIJSONSerializer
            receiver.setdefault("ui", {})["permissions"] = {
                "can_include_directly": can_include_directly
            }
        return obj

    @post_dump
    def hide_tombstone(self, obj, **kwargs):
        """Hide the tombstone information if it's not visible."""
        if not obj.get("tombstone", {}).get("is_visible", False):
            obj.pop("tombstone", None)

        return obj
