# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test views."""

from invenio_rdm_records.theme.views import doi_identifier, vocabulary_title


def test_vocabulary_title(app):
    # Valid key and vocabulary
    title = vocabulary_title({"role": "datamanager"}, 'contributors.role')
    assert title == "Data Manager"

    # Invalid vocabulary
    title = vocabulary_title({"role": "datamanager"}, 'garbage')
    assert title == ""

    # Invalid key
    title = vocabulary_title({"role": "garbage"}, 'contributor_role')
    assert title == ""


def test_doi_identifier():
    # DOI present
    identifiers = {
        "doi": "10.5281/zenodo.9999999",
        "arxiv": "9999.99999"
    }
    doi = doi_identifier(identifiers)
    assert "10.5281/zenodo.9999999" == doi

    # DOI absent
    identifiers = {
        "arxiv": "9999.99999"
    }
    doi = doi_identifier(identifiers)
    assert doi is None

    # Empty identifiers
    identifiers = {}
    doi = doi_identifier(identifiers)
    assert doi is None
