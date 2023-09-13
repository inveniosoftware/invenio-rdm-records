# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Journal serialization processing."""

from flask_resources.serializers import DumperMixin


class JournalDataciteDumper(DumperMixin):
    """Dumper for datacite serialization of 'Journal' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds the journal information as a related identifier in the DataCite metadata."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})

        if not journal_data:
            return data

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


class JournalDublinCoreDumper(DumperMixin):
    """Dumper for dublin core serialization of 'Journal' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized journal data to the input data under the 'sources' key."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})

        if not journal_data:
            return data

        title = journal_data.get("title")
        volume = journal_data.get("volume")
        issue = journal_data.get("issue")
        pages = journal_data.get("pages")
        year = _original.get("metadata", {}).get("publication_date")

        if volume and issue:
            volume = f"{volume}({issue})"

        if not volume:
            volume = issue

        parts = [
            title,
            volume,
            pages,
            f"({year})" if year else None,
        ]

        # Update input data with serialized data
        serialized_data = ", ".join([x for x in parts if x])
        sources = data.get("sources", [])
        sources.append(serialized_data)
        data["sources"] = sources

        return data


class JournalMarcXMLDumper(DumperMixin):
    """Dumper for MarcXML serialization of 'Journal' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized journal data to the input data under the '773' key."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})

        if not journal_data:
            return data

        items_dict = {}
        field_keys = {
            "p": journal_data.get("title"),
            "v": journal_data.get("volume"),
            "n": journal_data.get("issue"),
            "c": journal_data.get("pages"),
            "y": _original.get("metadata", {}).get("publication_date"),
        }
        for key, value in field_keys.items():
            if value:
                items_dict[key] = value

        if not items_dict:
            return data

        code = "909C4"
        existing_data = data.get(code)
        if existing_data and isinstance(existing_data, list):
            data[code].append(items_dict)
        else:
            data[code] = [items_dict]
        return data


class JournalCSLDumper(DumperMixin):
    """Dumper for CSL serialization of 'Journal' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized journal data to the input data."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})

        if not journal_data:
            return data

        title = journal_data.get("title")
        volume = journal_data.get("volume")
        issue = journal_data.get("issue")
        pages = journal_data.get("pages")
        issn = journal_data.get("issn")

        if title:
            data["container_title"] = title
        if pages:
            data["page"] = pages
        if volume:
            data["volume"] = volume
        if issue:
            data["issue"] = issue
        if issn:
            data["ISSN"] = issn

        return data


class JournalSchemaorgDumper(DumperMixin):
    """Dumper for Schemaorg serialization of 'Journal' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized journal data to the input data."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        journal_data = custom_fields.get("journal:journal", {})

        if not journal_data:
            return data

        title = journal_data.get("title")
        volume = journal_data.get("volume")
        issue = journal_data.get("issue")
        pages = journal_data.get("pages")
        issn = journal_data.get("issn")

        if title:
            data["container_title"] = title
        if pages:
            data["page"] = pages
        if volume:
            data["volume"] = volume
        if issue:
            data["issue"] = issue
        if issn:
            data["ISSN"] = issn

        return data
