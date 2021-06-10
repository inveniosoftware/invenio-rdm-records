# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSL based Schema for Invenio RDM Records."""

from edtf import parse_edtf
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import Schema, fields, missing
from marshmallow_utils.fields import SanitizedUnicode


class CSLCreatorSchema(Schema):
    """Creator/contributor common schema."""

    family = fields.Str(attribute="person_or_org.name")


class CSLJSONSchema(Schema):
    """CSL Marshmallow Schema."""

    id_ = SanitizedUnicode(data_key="id", attribute='id')
    type_ = fields.Method('get_type', data_key="type")
    title = SanitizedUnicode(attribute="metadata.title")
    abstract = SanitizedUnicode(attribute="metadata.description")
    author = fields.List(
        fields.Nested(CSLCreatorSchema), attribute='metadata.creators')
    issued = fields.Method('get_issued')
    language = fields.Method('get_language')
    version = SanitizedUnicode(attribute="metadata.version")
    note = fields.Method('get_note')
    doi = fields.Method('get_doi', data_key="DOI")
    isbn = fields.Method('get_isbn', data_key="ISBN")
    issn = fields.Method('get_issn', data_key="ISSN")
    publisher = SanitizedUnicode(attribute='metadata.publisher')

    def _read_resource_type(self, id_):
        """Retrieve resource type record using service."""
        return vocabulary_service.read(
            ('resource_types', id_),
            system_identity
        )._record

    def get_type(self, obj):
        """Get resource type."""
        resource_type = obj["metadata"]["resource_type"]
        resource_type_record = self._read_resource_type(resource_type["id"])
        props = resource_type_record["props"]
        return props.get("csl", "article")  # article is CSL "Other"

    def get_issued(self, obj):
        """Get issued dates."""
        date_parts = []
        publication_date = obj["metadata"]["publication_date"].split("/")
        for date in publication_date:
            p_date = parse_edtf(date)
            date_part = []
            year, month, day = p_date.year, p_date.month, p_date.day
            if year:
                date_part.append(year)
            if month:
                date_part.append(month)
            if day:
                date_part.append(day)

            date_parts.append(date_part)

        return {"date-parts": date_parts}

    def get_language(self, obj):
        """Get language."""
        metadata = obj["metadata"]
        languages = metadata.get("languages")

        return languages[0]["id"] if languages else missing

    def get_doi(self, obj):
        """Get DOI."""
        return obj["pids"].get("doi", {}).get("identifier", missing)

    def get_isbn(self, obj):
        """Get ISBN."""
        identifiers = obj["metadata"].get("identifiers", [])
        for identifier in identifiers:
            if identifier["scheme"] == "ISBN":
                return identifier["identifier"]

        return missing

    def get_issn(self, obj):
        """Get ISSN."""
        identifiers = obj["metadata"].get("identifiers", [])
        for identifier in identifiers:
            if identifier["scheme"] == "ISSN":
                return identifier["identifier"]

        return missing

    def get_note(self, obj):
        """Get note from funders."""
        funding = obj["metadata"].get("funding")
        if funding:
            funder = funding[0]["funder"]
            note = f"Funding by {funder['name']}"
            scheme = funder.get("scheme", "").upper()
            identifier = funder.get("identifier", "")

            if scheme:
                note = note + " " + scheme
            if identifier:
                note = note + " " + identifier + "."

            return note

        return missing
