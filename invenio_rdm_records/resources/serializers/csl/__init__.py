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
from flask_resources.serializers import MarshmallowJSONSerializer
from webargs import fields

from .schema import CSLJSONSchema


class CSLJSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based CSL JSON serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=CSLJSONSchema, **options)


def get_citation_string(json, id, style, locale):
    """Get the citation string from CiteProc library."""

    def _clean_result(text):
        """Remove double spaces, punctuation."""
        text = re.sub(r"\s\s+", " ", text)
        text = re.sub(r"\.\.+", ".", text)
        return text

    source = CiteProcJSON([json])
    citation_style = CitationStylesStyle(validate=False, style=style, locale=locale)
    bib = CitationStylesBibliography(citation_style, source, formatter.plain)
    citation = Citation([CitationItem(id)])
    bib.register(citation)

    return _clean_result(str(bib.bibliography()[0]))


def get_style_location(style):
    """Return the path to the CSL style if exists or throw."""
    try:
        return get_style_filepath(style.lower())
    except StyleNotFoundError as ex:
        current_app.logger.warning(f"CSL style {style} not found.")
        raise ex


class StringCitationSerializer(MarshmallowJSONSerializer):
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
        super().__init__(schema_cls=CSLJSONSchema, **options)
        self.url_args_retriever = url_args_retriever

    def serialize_object(self, record):
        """Serialize a single record.

        :param record: Record instance.
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

        return get_citation_string(
            self.dump_one(record), record["id"], style_filepath, locale
        )

    def serialize_object_list(self, records):
        """Serialize a list of records.

        :param records: List of records instance.
        """
        return "\n".join(
            [self.serialize_object(rec) for rec in records["hits"]["hits"]]
        )
