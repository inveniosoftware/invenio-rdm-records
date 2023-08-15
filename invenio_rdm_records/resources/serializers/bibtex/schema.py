# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BibTex based Schema for Invenio RDM Records."""

import datetime
import textwrap

from flask_resources.serializers import BaseSerializerSchema
from marshmallow import fields, post_dump
from slugify import slugify

from ..schemas import CommonFieldsMixin
from .errors import MissingRequiredFieldError
from .schema_formats import BibTexFormatter


class BibTexSchema(BaseSerializerSchema, CommonFieldsMixin):
    """Schema for records in BibTex."""

    id = fields.Str()
    resource_id = fields.Str(attribute="metadata.resource_type.id")
    version = fields.Str(attribute="metadata.version")
    date_created = fields.Method("get_date_created")
    locations = fields.Method("get_locations")
    titles = fields.Method("get_titles")
    doi = fields.Method("get_doi")
    creators = fields.Method("get_creators")
    creator_name = fields.Method("get_creator_name")
    publishers = fields.Method("get_publishers")
    contributors = fields.Method("get_contributors")
    school = fields.Str(attribute="custom_fields.thesis:university")
    journal_title = fields.Str(attribute="custom_fields.journal:journal.title")
    journal_volume = fields.Str(attribute="custom_fields.journal:journal.volume")
    journal_issue = fields.Str(attribute="custom_fields.journal:journal.issue")
    journal_pages = fields.Method("get_journal_or_imprint_pages")

    def get_journal_or_imprint_pages(self, obj):
        """Get journal or imprint pages."""
        journal_pages = (
            obj.get("custom_fields", {}).get("journal:journal", {}).get("pages")
        )
        imprint_pages = (
            obj.get("custom_fields", {}).get("imprint:imprint", {}).get("pages")
        )
        return journal_pages or imprint_pages

    def get_date_created(self, obj):
        """Get date last updated."""
        date_obj = datetime.datetime.fromisoformat(obj["created"])

        month = date_obj.strftime("%b").lower()
        year = date_obj.strftime("%Y")
        return {"month": month, "year": year}

    def get_creator_name(self, obj):
        """Get creator name."""
        return obj["metadata"]["creators"][0]["person_or_org"]["name"]

    @post_dump()
    def format_record(self, data, many, **kwargs):
        """Format Record depending on its type."""
        format = data["resource_id"]
        format = format.replace("-", "_")

        if hasattr(BibTexFormatter, format):
            # If this format has "custom" parser fields, use them
            bib_fields = getattr(BibTexFormatter, format)()
        else:
            bib_fields = BibTexFormatter.other()  # Default parser fields

        out = "@" + bib_fields.pop("name") + "{"
        out += self._get_citation_key(data) + ",\n"
        try:
            inp = self._fetch_fields(data, bib_fields)
        except MissingRequiredFieldError:
            # Fallback to default
            inp = self._fetch_fields(data, BibTexFormatter.other())
        out += self._clean_input(inp)
        out += "}"
        return out

    def _fetch_fields(self, data, bib_fields):
        req_fields = bib_fields["req_fields"]
        non_req_fields = bib_fields.get("opt_fields", []) + ["doi", "url"]

        # The following fields are taken from Zenodo for consistency/compatibility reasons
        fields = {
            "address": data.get("locations", None),  # Done
            "author": data.get("creators", None),  # Done
            "publisher": (
                lambda publishers: None if publishers is None else publishers[0]
            )(
                data.get("publishers", None)
            ),  # Done
            "title": (lambda titles: None if titles is None else titles[0])(
                data.get("titles", None)
            ),  # Done
            "year": data.get("date_created", {}).get("year", None),  # Done
            "doi": data.get("doi", None),  # Done
            "month": data.get("date_created", {}).get("month", None),  # Done
            "version": data.get("version", None),  # Done
            "url": (lambda doi: None if doi is None else "https://doi.org/" + doi)(
                data.get("doi", None)
            ),  # Done
            "school": data.get("school", None),
            "journal": data.get("journal_title", None),
            "volume": data.get("journal_volume", None),
            "number": data.get("journal_issue", None),
            "pages": data.get("journal_pages", None),
            "note": data.get("note", None),  # [TODO] Implement once notes are merged
            "venue": data.get(
                "venue", None
            ),  # [TODO] Zenodo backward compatibility issue
        }

        out = ""
        for field in req_fields + non_req_fields:
            value = fields[field]
            if value is not None:
                out += self._format_output_row(field, value)
            elif value is None and field in req_fields:
                raise MissingRequiredFieldError(field)
        return out

    def _format_output_row(self, field, value):
        out = ""
        if isinstance(value, str):
            value = value.strip()
        if field == "author":
            out += "  {0:<12} = ".format(field) + "{"
            out += value[0] + (" and\n" if len(value) > 1 else "")
            out += " and\n".join(
                [" {0:<16} {1:<}".format("", line) for line in value[1::]]
            )
            out += "},\n"

        elif len(value) > 50:
            wrapped = textwrap.wrap(value, 50)
            out = "  {0:<12} = {{{{{1} \n".format(field, wrapped[0])
            for line in wrapped[1:-1]:
                out += " {0:<17} {1:<}\n".format("", line)
            out += " {0:<17} {1:<}}}}},\n".format("", wrapped[-1])
        elif field == "month":
            out = "  {0:<12} = {1},\n".format(field, value)
        elif field == "url":
            out == "  {0:<12} = {{{1}}}\n".format(field, value)
        else:
            if not isinstance(value, list) and value.isdigit():
                out = "  {0:<12} = {1},\n".format(field, value)
            else:
                out = "  {0:<12} = {{{1}}},\n".format(field, value)
        return out

    def _get_citation_key(self, data):
        """Return citation key."""
        id = data["id"]
        name = data["creator_name"]
        pubdate = data.get("date_created", {}).get("year", None)
        year = id
        if pubdate is not None:
            year = "{}_{}".format(pubdate, id)
        return "{0}_{1}".format(slugify(name, separator="_", max_length=40), year)

    def _clean_input(self, input):
        unsupported_chars = ["&", "%", "$", "_", "#"]
        chars = list(input)
        for index, char in enumerate(chars):
            if char in unsupported_chars:
                chars[index] = "\\" + chars[index]
        return "".join(chars)
