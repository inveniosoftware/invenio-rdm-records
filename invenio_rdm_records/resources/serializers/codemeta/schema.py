# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Codemeta schema."""

from edtf import parse_edtf
from edtf.parser.grammar import ParseException
from marshmallow import fields, missing
from pydash import py_

from ..schemaorg.schema import SchemaorgSchema


class CodemetaSchema(SchemaorgSchema):
    """CodeMeta schema.

    CodeMeta schema derives from Schema.org
    """

    identifier = fields.Method("get_id")
    context = fields.Constant(
        "https://doi.org/10.5063/schema/codemeta-2.0", data_key="@context"
    )
    funding = fields.Method("get_funding")
    embargoDate = fields.Method("get_embargo_date", data_key="embargoDate")

    def get_funding(self, obj):
        """Funding CodeMeta schema."""
        funding = obj.get("metadata", {}).get("funding", [])
        if not funding:
            return missing

        result = None
        for fund in funding:
            award = fund.get("award", {})
            title = award.get("title", {}).get("en")
            number = award.get("number")
            grant_url = next(
                (
                    x["identifier"]
                    for x in award.get("identifiers", [])
                    if x["scheme"] == "url"
                ),
                None,
            )
            if grant_url or (title and number):
                result = grant_url or f"{title} ({number})"
                break

        return result or missing

    def get_embargo_date(self, obj):
        """Get embargo date."""
        is_embargo = py_.get(obj, "access.embargo.active")

        if not is_embargo:
            return missing

        parsed_date = None
        try:
            parsed_date = parse_edtf(py_.get(obj, "access.embargo"))
        except ParseException:
            pass
        return parsed_date or missing
