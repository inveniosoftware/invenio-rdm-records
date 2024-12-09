# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BibTex Schema formaters, helper file for schema.py file."""


class BibTexFormatter:
    """Formater class for bibtex.

    It defines each bibtex entry type supported by the default biblatex data model along with the fields supported by each type.

    .. seealso::

        Entry types follow the specification from https://mirror.foobar.to/CTAN/macros/latex/contrib/biblatex/doc/biblatex.pdf and legacy Zenodo.
    """

    book = {
        "name": "book",
        "req_fields": ["author", "title", "publisher", "year"],
        "opt_fields": ["volume", "address", "month", "note", "doi", "url"],
    }
    """A single-volume book."""

    booklet = {
        "name": "booklet",
        "req_fields": ["title"],
        "opt_fields": ["author", "address", "month", "year", "note", "doi", "url"],
    }
    """A book-like work without a formal publisher or sponsoring institution."""

    misc = {
        "name": "misc",
        "req_fields": [],
        "opt_fields": [
            "author",
            "title",
            "month",
            "year",
            "note",
            "publisher",
            "version",
            "doi",
            "url",
        ],
    }
    """A fallback type for entries which do not fit into any other category."""

    in_proceedings = {
        "name": "inproceedings",
        "req_fields": ["author", "title", "booktitle", "year"],
        "opt_fields": [
            "pages",
            "publisher",
            "address",
            "month",
            "note",
            "venue",
            "doi",
            "url",
        ],
    }
    """An article in a conference proceedings."""

    proceedings = {
        "name": "proceedings",
        "req_fields": ["title", "year"],
        "opt_fields": ["publisher", "address", "month", "note", "doi", "url"],
    }
    """A single-volume conference proceedings."""

    article = {
        "name": "article",
        "req_fields": ["author", "title", "journal", "year"],
        "opt_fields": ["volume", "number", "pages", "month", "note", "doi", "url"],
    }
    """An article in a journal, magazine, newspaper, or other periodical which forms a self-contained unit with its own title."""

    unpublished = {
        "name": "unpublished",
        "req_fields": ["author", "title", "note"],
        "opt_fields": ["month", "year", "doi", "url"],
    }
    """A work with an author and a title which has not been formally published."""

    thesis = {
        "name": "phdthesis",
        "req_fields": ["author", "title", "school", "year"],
        "opt_fields": ["address", "month", "note", "doi", "url"],
    }
    """A thesis written for an educational institution."""

    manual = {
        "name": "manual",
        "req_fields": ["title"],
        "opt_fields": ["author", "address", "month", "year", "note", "doi", "url"],
    }
    """Technical or other documentation, not necessarily in printed form."""

    dataset = {
        "name": "dataset",
        "req_fields": [],
        "opt_fields": [
            "author",
            "title",
            "month",
            "year",
            "note",
            "publisher",
            "version",
            "doi",
            "url",
        ],
    }
    """A data set or a similar collection of (mostly) raw data."""

    software = {
        "name": "software",
        "req_fields": [],
        "opt_fields": [
            "author",
            "title",
            "month",
            "year",
            "note",
            "publisher",
            "version",
            "doi",
            "url",
            "swhid",
        ],
    }
    """Computer software."""
