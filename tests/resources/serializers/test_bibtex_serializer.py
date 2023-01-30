# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from collections import Iterable

import pytest

from invenio_rdm_records.resources.serializers.bibtex import BibtexSerializer


@pytest.fixture(scope="function")
def updated_minimal_record(minimal_record):
    """Update fields (done after record create) for BibTex serializer."""
    minimal_record["access"]["status"] = "open"
    minimal_record["created"] = "2023-03-09T00:00:00.000000+00:00"
    minimal_record["id"] = "abcde-fghij"

    for creator in minimal_record["metadata"]["creators"]:
        name = creator["person_or_org"].get("name")
        if not name:
            creator["person_or_org"]["name"] = "Name"

    return minimal_record


@pytest.fixture(scope="function")
def updated_full_record(full_record):
    """Update fields (done after record create) for BibTex serializer."""
    full_record["access"]["status"] = "embargoed"
    full_record["created"] = "2023-03-23T00:00:00.000000+00:00"
    full_record["id"] = "abcde-fghij"
    full_record["metadata"]["resource_type"]["id"] = "other"

    return full_record


def test_bibtex_serializer_minimal_record(running_app, updated_minimal_record):
    """Test serializer for BibTex"""
    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\
@misc{brown_2023_abcde-fghij,\n\
  author       = {Name and\n\
                  Troy Inc.},\n\
  title        = {A Romans story},\n\
  month        = mar,\n\
  year         = 2023,\n\
  publisher    = {Acme Inc},\n\
}"

    assert serialized_record == expected_data


def test_bibtex_serializer_full_record(running_app, updated_full_record):
    """Test serializer for BibTex"""
    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_full_record)

    expected_data = "\
@misc{nielsen_2023_abcde-fghij,\n\
  author       = {Nielsen, Lars Holm},\n\
  title        = {InvenioRDM},\n\
  month        = mar,\n\
  year         = 2023,\n\
  publisher    = {InvenioRDM},\n\
  version      = {v1.0},\n\
}"

    assert serialized_record == expected_data
