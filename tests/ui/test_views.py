# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test views."""

import datetime

import pytest

from invenio_rdm_records.theme.views import doi_identifier, \
    doi_locally_managed, to_date, vocabulary_title


def test_vocabulary_title(app):
    # Valid key and vocabulary
    title = vocabulary_title({"role": "DataManager"}, 'contributors.role')
    assert title == "Data Manager"

    # Invalid vocabulary
    title = vocabulary_title({"role": "DataManager"}, 'garbage')
    assert title == ""

    # Invalid key
    title = vocabulary_title({"role": "garbage"}, 'contributor_role')
    assert title == ""


def test_to_date():
    # Valid date_string
    date_string = "2020-08-27"
    date = to_date(date_string)
    assert datetime.date(2020, 8, 27) == date

    # Non-string date_string
    with pytest.raises(AssertionError):
        date_string = None
        date = to_date(date_string)

    # Invalid date_string
    date_string = "garbage"
    date = to_date(date_string)
    assert date == "garbage"


def test_doi_identifier():
    # DOI present
    identifiers = {
        "DOI": "10.5281/zenodo.9999999",
        "arXiv": "9999.99999"
    }
    doi = doi_identifier(identifiers)
    assert "10.5281/zenodo.9999999" == doi

    # DOI absent
    identifiers = {
        "arXiv": "9999.99999"
    }
    doi = doi_identifier(identifiers)
    assert doi is None

    # Empty identifiers
    identifiers = {}
    doi = doi_identifier(identifiers)
    assert doi is None


def test_doi_locally_managed(app):
    # DOI is locally managed
    assert doi_locally_managed("10.9999/zenodo.9999999")

    # DOI is not locally managed
    assert not doi_locally_managed("10.5281/zenodo.9999999")
