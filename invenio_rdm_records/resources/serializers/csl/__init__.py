# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSL JSON and  citation string serializers for Invenio RDM Records."""

import re

from citeproc import (
    Citation,
    CitationItem,
    CitationStylesBibliography,
    CitationStylesStyle,
    formatter,
)
from citeproc.source.json import CiteProcJSON
from citeproc_styles import get_style_filepath
from citeproc_styles.errors import StyleNotFoundError
from flask import current_app
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer
from webargs import fields

from ....contrib.imprint.processors import ImprintCSLDumper
from ....contrib.journal.processors import JournalCSLDumper
from ....contrib.meeting.processors import MeetingCSLDumper
from .schema import CSLJSONSchema


class CSLJSONSerializer(MarshmallowSerializer):
    """Marshmallow based CSL JSON serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=CSLJSONSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                "dumpers": [JournalCSLDumper(), ImprintCSLDumper(), MeetingCSLDumper()]
            },  # Order matters
            **options,
        )


def get_citation_string(json, id, style, locale):
    """Get the citation string from CiteProc library."""

    def _clean_result(text):
        """Remove double spaces, punctuation."""
        text = re.sub(r"\s\s+", " ", text)
        text = re.sub(r"\.\.+", ".", text)
        return text

    def _replace_doi_link(text, doi, new_doi_link):
        """Replace the citation DOI link with the correct one.

        Citation styles that generate a DOI URL in their citation generate it with the
        form: "https://doi.org/<prefix>/<suffix>". However, when using a
        Datacite test account (i.e. when `DATACITE_TEST_MODE = True`) and
        potentially when using other providers' test accounts, the actual DOI URL is
        of a different form: "https://handle.test.datacite.org/<prefix>/<suffix> as of
        writing. By relying on a passed DOI URL instead, we can make sure the
        correct URL is used. The DOI url is passed in the namespaced entry
        json["_extras"]["links"]["doi"].
        """
        if doi and new_doi_link:
            return text.replace(f"https://doi.org/{doi}", new_doi_link)
        else:
            return text

    extras = json.pop("_extras", {})
    source = CiteProcJSON([json])
    citation_style = CitationStylesStyle(validate=False, style=style, locale=locale)
    bib = CitationStylesBibliography(citation_style, source, formatter.plain)
    citation = Citation([CitationItem(id)])
    bib.register(citation)

    citation_raw = str(bib.bibliography()[0])
    citation_doi_replaced = _replace_doi_link(
        citation_raw,
        json.get("DOI"),
        extras.get("links", {}).get("doi"),
    )
    return _clean_result(citation_doi_replaced)


def get_style_location(style):
    """Return the path to the CSL style if exists or throw."""
    try:
        return get_style_filepath(style.lower())
    except StyleNotFoundError as ex:
        current_app.logger.warning(f"CSL style {style} not found.")
        raise ex


class StringCitationSerializer(MarshmallowSerializer):
    """CSL Citation Formatter serializer for records.

    In order to produce a formatted citation of a record through citeproc-py,
    we need a CSL-JSON serialized version of it.
    """

    _default_style = "harvard1"
    """The `citeproc-py` library supports by default the 'harvard1' style."""

    _default_locale = "en-US"
    """The `citeproc-py` library supports by default the 'harvard1' style."""

    _user_args = {
        "style": fields.Str(load_default=_default_style),
        "locale": fields.Str(load_default=_default_locale),
    }
    """Arguments for the webargs parser."""

    _valid_formats = ("csl", "bibtex")
    """Supported formats by citeproc-py."""

    def __init__(self, url_args_retriever, **options):
        """Constructor.

        :param url_args_retriever: callable func or object that return the
                                   style and locale URL args
        """
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=CSLJSONSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                "dumpers": [JournalCSLDumper(), ImprintCSLDumper(), MeetingCSLDumper()]
            },  # Order matters
            **options,
        )
        self.url_args_retriever = url_args_retriever

    def serialize_object(self, record):
        """Serialize the output of a RecordItem.to_dict() to a citation string.

        :param record: dict from RecordItem.to_dict().
        """
        style, locale = (
            self.url_args_retriever()
            if callable(self.url_args_retriever)
            else self.url_args_retriever
        )
        # set defaults if params are not provided
        style = style or self._default_style
        locale = locale or self._default_locale

        style_filepath = get_style_location(style)

        # Pass the record links under _extras namespace
        # so that DOI link can be replaced
        record_dumped = self.dump_obj(record)
        record_dumped.setdefault("_extras", {})
        record_dumped["_extras"]["links"] = record.get("links", {})

        return get_citation_string(record_dumped, record["id"], style_filepath, locale)

    def serialize_object_list(self, records):
        """Serialize a list of records.

        :param records: List of records instance.
        """
        return "\n".join(
            [self.serialize_object(rec) for rec in records["hits"]["hits"]]
        )
