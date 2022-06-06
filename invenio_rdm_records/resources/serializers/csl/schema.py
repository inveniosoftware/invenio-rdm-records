# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSL based Schema for Invenio RDM Records."""

from edtf import parse_edtf
from edtf.parser.edtf_exceptions import EDTFParseException
from edtf.parser.parser_classes import Date, Interval
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import Schema, fields, missing, pre_dump
from marshmallow_utils.fields import SanitizedUnicode, StrippedHTML

from ..utils import get_preferred_identifier


class CSLCreatorSchema(Schema):
    """Creator/contributor common schema."""

    family = fields.Str(attribute="person_or_org.family_name")
    given = fields.Str(attribute="person_or_org.given_name")

    @pre_dump
    def update_names(self, data, **kwargs):
        """Organizational creators do not have family/given name."""
        # family is required by CSL
        if not data.get("person_or_org").get("family_name"):
            name = data["person_or_org"]["name"]
            data["person_or_org"]["family_name"] = name

        return data


def add_if_not_none(year, month, day):
    """Adds year, month a day to a list if each are not None."""
    _list = []
    _list.append(year) if year else None
    _list.append(month) if month else None
    _list.append(day) if day else None
    return _list


class CSLJSONSchema(Schema):
    """CSL Marshmallow Schema."""

    id_ = SanitizedUnicode(data_key="id", attribute="id")
    type_ = fields.Method("get_type", data_key="type")
    title = SanitizedUnicode(attribute="metadata.title")
    abstract = StrippedHTML(attribute="metadata.description")
    author = fields.List(fields.Nested(CSLCreatorSchema), attribute="metadata.creators")
    issued = fields.Method("get_issued")
    language = fields.Method("get_language")
    version = SanitizedUnicode(attribute="metadata.version")
    note = fields.Method("get_note")
    doi = fields.Method("get_doi", data_key="DOI")
    isbn = fields.Method("get_isbn", data_key="ISBN")
    issn = fields.Method("get_issn", data_key="ISSN")
    publisher = SanitizedUnicode(attribute="metadata.publisher")

    def _read_resource_type(self, id_):
        """Retrieve resource type record using service."""
        rec = vocabulary_service.read(system_identity, ("resourcetypes", id_))
        return rec._record

    def get_type(self, obj):
        """Get resource type."""
        resource_type = obj["metadata"].get(
            "resource_type", {"id": "publication-article"}
        )

        resource_type_record = self._read_resource_type(resource_type["id"])
        props = resource_type_record["props"]
        return props.get("csl", "article")  # article is CSL "Other"

    def get_issued(self, obj):
        """Get issued dates."""
        try:
            parsed = parse_edtf(obj["metadata"].get("publication_date"))
        except EDTFParseException:
            return missing

        if isinstance(parsed, Date):
            parts = add_if_not_none(parsed.year, parsed.month, parsed.day)
            return {"date-parts": [parts]}
        elif isinstance(parsed, Interval):
            d1 = parsed.lower
            d2 = parsed.upper
            return {
                "date-parts": [
                    add_if_not_none(d1.year, d1.month, d1.day),
                    add_if_not_none(d2.year, d2.month, d2.day),
                ]
            }
        else:
            return missing

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
            id_ = funder.get("id")
            if id_:
                funder_service = current_service_registry.get("funders")
                funder = funder_service.read(system_identity, id_).to_dict()

            note = f"Funding by {funder['name']}"
            identifiers = funder.get("identifiers", [])
            identifier = get_preferred_identifier(
                priority=("ror", "grid", "doi", "isni", "gnd"), identifiers=identifiers
            )

            if identifier:
                note += (
                    f" {identifier['scheme'].upper()} " f"{identifier['identifier']}."
                )
            return note

        return missing
