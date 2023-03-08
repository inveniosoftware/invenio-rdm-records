# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021-2023 Graz University of Technology.
# Copyright (C) 2022 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from copy import deepcopy
from functools import partial

from flask import current_app, g
from flask_resources import BaseObjectSchema
from invenio_communities.communities.resources.ui_schema import (
    _community_permission_check,
)
from invenio_i18n import get_locale
from invenio_records_resources.services.custom_fields import CustomFieldsSchemaUI
from invenio_vocabularies.contrib.awards.serializer import AwardL10NItemSchema
from invenio_vocabularies.contrib.funders.serializer import FunderL10NItemSchema
from invenio_vocabularies.resources import L10NString, VocabularyL10Schema
from marshmallow import Schema, fields, missing, pre_dump
from marshmallow_utils.fields import FormatDate as FormatDate_
from marshmallow_utils.fields import FormatEDTF as FormatEDTF_
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode, StrippedHTML
from marshmallow_utils.fields.babel import gettext_from_dict

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


def make_affiliation_index(attr, obj, dummy_ctx):
    """Serializes creators/contributors for easier UI consumption."""
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


class MeetingSchema(Schema):
    """Schema for dumping 'meeting' custom field in the UI."""

    acronym = SanitizedUnicode()
    dates = SanitizedUnicode()
    place = SanitizedUnicode()
    session_part = SanitizedUnicode()
    session = SanitizedUnicode()
    title = SanitizedUnicode()
    url = SanitizedUnicode()


def compute_publishing_information(obj, dummyctx):
    """Computes 'publishing information' string from custom fields."""

    def _format_journal(journal, publication_date):
        """Formats a journal object into a string based on its attributes.

        Example:
            _format_journal({"title": "The Effects of Climate Change", "volume": 10, "issue": 2, "pages": "15-22", "issn": "1234-5678"}, "2022")
            >>> 'The Effects of Climate Change: 10 (2022) no. 1234-5678 pp. 15-22 (2)'
        """
        journal_title = journal.get("title")
        if not journal_title:
            return ""

        journal_issn = journal.get("issn")
        journal_issue = journal.get("issue")
        journal_pages = journal.get("pages")
        publication_date = f"({publication_date})" if publication_date else None
        title = f"{journal_title}:"
        issn = f"no. {journal_issn}" if journal_issn else None
        issue = f"({journal_issue})" if journal_issue else None
        pages = f"pp. {journal_pages}" if journal_pages else None
        fields = [title, journal.get("volume"), publication_date, issn, pages, issue]
        formatted = " ".join(filter(None, fields))

        return formatted if formatted else ""

    def _format_imprint(imprint, publisher):
        """Formats a imprint object into a string based on its attributes."""
        place = imprint.get("place", "")
        isbn = imprint.get("isbn", "")
        formatted = "{publisher}{place} {isbn}".format(
            publisher=publisher, place=f", {place}", isbn=f"({isbn})"
        )
        return formatted

    attr = "custom_fields"
    field = obj.get(attr, {})
    publication_date = obj.get("metadata", {}).get("publication_date")
    publisher = obj.get("metadata", {}).get("publisher")

    # Retrieve publishing related custom fields
    journal = field.get("journal:journal")
    imprint = field.get("imprint:imprint")
    thesis = field.get("thesis:university")

    result = {}
    if journal:
        journal_string = _format_journal(journal, publication_date)
        if journal_string:
            result.update({"journal": journal_string})

    if imprint and publisher:
        imprint_string = _format_imprint(imprint, publisher)
        result.update({"imprint": imprint_string})

    if thesis:
        result.update({"thesis": thesis})

    if len(result.keys()) == 0:
        return missing

    return result


class UIRecordSchema(BaseObjectSchema):
    """Schema for dumping extra information for the UI."""

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
