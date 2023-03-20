#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Journal custom fields.

Implements the following fields:
- journal.issue
- journal.pages
- journal.title
- journal.volume
"""

from idutils import is_issn
from abc import ABC

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields, missing
from marshmallow_utils.fields import SanitizedUnicode


class DumpProcessorMixin(ABC):
    """Mixin class that defines pre_dump and post_dump methods to extend records serialization."""

    def post_dump(self, data, original={}, **kwargs):
        """Hook called after the marshmallow serialization of the record.

        :param data: The dumped record data.
        :param original: The original record data.
        :param kwargs: Additional keyword arguments.
        :returns: The serialized record data.
        """
        return data

    def pre_dump(self, data, original={}, **kwargs):
        """
        Hook called before the marshmallow serialization of the record.

        :param data: The record data to dump.
        :param original: The original record data.
        :param kwargs: Additional keyword arguments.
        :returns: The data to dump.
        """
        return data


class JournalDataciteProcessor(DumpProcessorMixin):
    """Dump processor for datacite serialization of 'Journal' custom field."""

    def post_dump(self, data, original={}, **kwargs):
        """Adds the journal information as a related identifier in the DataCite metadata."""
        custom_fields = original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})
        issn = journal_data.get("issn")

        # Only dumps if 'issn' is set.
        if not issn:
            return data

        # Serialize journal
        relationType = "IsPartOf"
        resourceTypeGeneral = "Collection"
        relatedIdentifierType = "ISSN"

        serialized_journal = {
            "relatedIdentifier": issn,
            "relationType": relationType,
            "relatedIdentifierType": relatedIdentifierType,
            "resourceTypeGeneral": resourceTypeGeneral,
        }

        # Update input data
        related_identifiers = data.get("relatedIdentifiers", [])
        related_identifiers.append(serialized_journal)
        data["relatedIdentifiers"] = related_identifiers

        return data


class JournalDublinCoreProcessor(DumpProcessorMixin):
    """Dump processor for dublin core serialization of 'Journal' custom field."""

    def post_dump(self, data, original={}, **kwargs):
        """Adds serialized journal data to the input data under the 'sources' key."""
        custom_fields = original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})
        title = journal_data.get("title")
        volume = journal_data.get("volume")
        issue = journal_data.get("issue")
        pages = journal_data.get("pages")
        year = original.get("metadata", {}).get("publication_date")

        if volume and issue:
            volume = f"{volume}({issue})"

        if not volume:
            volume = issue

        parts = [
            title,
            volume,
            pages,
            "({0})".format(year) if year else None,
        ]

        # Update input data with serialized data
        serialized_data = ", ".join([x for x in parts if x])
        sources = data.get("sources", [])
        sources.append(serialized_data)
        data["sources"] = sources

        return data


class JournalMarcXMLProcessor(DumpProcessorMixin):
    """Dump processor for MarcXML serialization of 'Journal' custom field."""

    def post_dump(self, data, original={}, **kwargs):
        """Adds serialized journal data to the input data under the '773' key."""
        custom_fields = original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})

        if not journal_data:
            return data

        items_dict = {}

        title = journal_data.get("title")
        if title:
            items_dict["p"] = title

        volume = journal_data.get("volume")
        if volume:
            items_dict["v"] = volume

        issue = journal_data.get("issue")
        if issue:
            items_dict["n"] = issue

        pages = journal_data.get("pages")
        if pages:
            items_dict["c"] = pages

        year = original.get("metadata", {}).get("publication_date")
        if year:
            items_dict["y"] = year

        if not items_dict:
            return data

        # TODO in zenodo, journal field serializes to
        # TODO code 909, C, 4 but that's not in the specification
        code = "773  "

        data[code] = items_dict
        return data


class JournalCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Journal fields definitions."""
        return fields.Nested(
            {
                "title": SanitizedUnicode(),
                "issue": SanitizedUnicode(),
                "volume": SanitizedUnicode(),
                "pages": SanitizedUnicode(),
                "issn": SanitizedUnicode(
                    validate=is_issn,
                    error_messages={
                        "validator_failed": _("Please provide a valid ISSN.")
                    },
                ),
            }
        )

    @property
    def mapping(self):
        """Journal search mappings."""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "issue": {"type": "keyword"},
                "pages": {"type": "keyword"},
                "volume": {"type": "keyword"},
                "issn": {"type": "keyword"},
            },
        }


JOURNAL_NAMESPACE = {
    # Journal
    "journal": "",
}


JOURNAL_CUSTOM_FIELDS = [
    JournalCF(name="journal:journal"),
]

JOURNAL_CUSTOM_FIELDS_UI = {
    "section": _("Journal"),
    "fields": [
        {
            "field": "journal:journal",
            "ui_widget": "Journal",
            "template": "journal.html",
            "props": {
                "label": _("Journal"),
                "title": {
                    "label": _("Title"),
                    "placeholder": "",
                    "description": _(
                        "Title of the journal on which the article was published"
                    ),
                },
                "volume": {
                    "label": _("Volume"),
                    "placeholder": "",
                    "description": "",
                },
                "issue": {
                    "label": _("Issue"),
                    "placeholder": "",
                    "description": "",
                },
                "pages": {
                    "label": _("Pages"),
                    "placeholder": "",
                    "description": "",
                },
                "issn": {
                    "label": _("ISSN"),
                    "placeholder": "",
                    "description": _("International Standard Serial Number"),
                },
                "icon": "newspaper outline",
            },
        }
    ],
}
