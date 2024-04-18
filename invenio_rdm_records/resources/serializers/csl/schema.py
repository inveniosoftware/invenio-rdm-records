# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSL based Schema for Invenio RDM Records."""

from babel_edtf import parse_edtf
from edtf.parser.edtf_exceptions import EDTFParseException
from edtf.parser.parser_classes import Date, Interval
from flask_resources.serializers import BaseSerializerSchema
from marshmallow import Schema, fields, missing, pre_dump
from marshmallow_utils.fields import SanitizedUnicode, StrippedHTML
from pydash import py_

from ..schemas import CommonFieldsMixin
from ..utils import get_vocabulary_props


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


class CSLJSONSchema(BaseSerializerSchema, CommonFieldsMixin):
    """CSL Marshmallow Schema."""

    id_ = SanitizedUnicode(data_key="id", attribute="id")
    type_ = fields.Method("get_type", data_key="type")
    title = SanitizedUnicode(attribute="metadata.title")
    abstract = StrippedHTML(attribute="metadata.description")
    author = fields.List(fields.Nested(CSLCreatorSchema), attribute="metadata.creators")
    issued = fields.Method("get_issued")
    language = fields.Method("get_language")
    version = SanitizedUnicode(attribute="metadata.version")
    doi = fields.Method("get_doi", data_key="DOI")
    isbn = fields.Method("get_isbn", data_key="ISBN")
    issn = fields.Method("get_issn", data_key="ISSN")
    publisher = SanitizedUnicode(attribute="metadata.publisher")

    def get_type(self, obj):
        """Get resource type."""
        resource_type_id = py_.get(obj, "metadata.resource_type.id")
        if not resource_type_id:
            return missing

        props = get_vocabulary_props(
            "resourcetypes",
            [
                "props.csl",
            ],
            resource_type_id,
        )
        return props.get("csl", "article")  # article is CSL "Other"

    def get_issued(self, obj):
        """Get issued dates."""
        publication_date = py_.get(obj, "metadata.publication_date")
        if not publication_date:
            return missing

        try:
            parsed = parse_edtf(publication_date)
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

    def get_isbn(self, obj):
        """Get ISBN."""
        identifiers = obj["metadata"].get("identifiers", [])
        for identifier in identifiers:
            if identifier["scheme"] == "isbn":
                return identifier["identifier"]

        return missing

    def get_issn(self, obj):
        """Get ISSN."""
        identifiers = obj["metadata"].get("identifiers", [])
        for identifier in identifiers:
            if identifier["scheme"] == "issn":
                return identifier["identifier"]

        return missing
