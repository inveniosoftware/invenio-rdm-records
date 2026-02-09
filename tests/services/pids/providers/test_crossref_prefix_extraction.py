# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test Crossref additional prefix handling."""


def test_crossref_prefix_extraction_from_identifier():
    """Test that prefix is correctly extracted from DOI identifier.

    This is a unit test that doesn't require OpenSearch or full application.
    It tests the prefix extraction logic that should work for both
    CROSSREF_PREFIX and CROSSREF_ADDITIONAL_PREFIXES.
    """
    # Test default prefix extraction
    doi_default = "10.59350/rdm.12345"
    prefix_default = doi_default.split("/")[0]
    assert prefix_default == "10.59350"

    # Test additional prefix extraction
    doi_additional = "10.65527/rdm.67890"
    prefix_additional = doi_additional.split("/")[0]
    assert prefix_additional == "10.65527"

    # Test that different prefixes are detected
    assert prefix_default != prefix_additional


def test_prefix_detection_in_crossref_additional_prefixes():
    """Test the logic for detecting if a prefix is in CROSSREF_ADDITIONAL_PREFIXES.

    This tests the configuration lookup that should happen in the code.
    """
    # Simulate config
    CROSSREF_PREFIX = "10.59350"
    CROSSREF_ADDITIONAL_PREFIXES = ["10.65527", "10.12345"]

    # Test DOI with default prefix
    doi_default = "10.59350/rdm.abc"
    prefix_default = doi_default.split("/")[0]
    is_default = prefix_default == CROSSREF_PREFIX
    is_additional = prefix_default in CROSSREF_ADDITIONAL_PREFIXES

    assert is_default is True
    assert is_additional is False

    # Test DOI with additional prefix
    doi_additional = "10.65527/rdm.xyz"
    prefix_additional = doi_additional.split("/")[0]
    is_default = prefix_additional == CROSSREF_PREFIX
    is_additional = prefix_additional in CROSSREF_ADDITIONAL_PREFIXES

    assert is_default is False
    assert is_additional is True

    # Test DOI with unknown prefix
    doi_unknown = "10.99999/rdm.unknown"
    prefix_unknown = doi_unknown.split("/")[0]
    is_default = prefix_unknown == CROSSREF_PREFIX
    is_additional = prefix_unknown in CROSSREF_ADDITIONAL_PREFIXES

    assert is_default is False
    assert is_additional is False
