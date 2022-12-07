# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers.dublincore import (
    DublinCoreJSONSerializer,
    DublinCoreXMLSerializer,
)
from invenio_rdm_records.resources.serializers.errors import VocabularyItemNotFoundError


@pytest.fixture(scope="function")
def updated_full_record(full_record):
    """Update fields (done after record create) for Dublin Core serializer."""
    full_record["access"]["status"] = "embargoed"

    return full_record


@pytest.fixture(scope="function")
def updated_minimal_record(minimal_record):
    """Update fields (done after record create) for Dublin Core serializer."""
    minimal_record["access"]["status"] = "open"
    for creator in minimal_record["metadata"]["creators"]:
        name = creator["person_or_org"].get("name")
        if not name:
            creator["person_or_org"]["name"] = "Name"

    return minimal_record


def test_dublincorejson_serializer(running_app, updated_full_record):
    """Test serializer to Dublin Core JSON"""
    expected_data = {
        "contributors": ["Nielsen, Lars Holm"],
        "types": ["info:eu-repo/semantic/other"],
        "relations": ["doi:10.1234/foo.bar"],
        "descriptions": ["A description \nwith HTML tags", "Bla bla bla"],
        "identifiers": ["1924MNRAS..84..308E", "10.5281/inveniordm.1234"],
        "publishers": ["InvenioRDM"],
        "languages": ["dan", "eng"],
        "formats": ["application/pdf"],
        "titles": ["InvenioRDM"],
        "creators": ["Nielsen, Lars Holm"],
        "subjects": ["custom"],
        "dates": ["2018/2020-09", "info:eu-repo/date/embargoEnd/2131-01-01"],
        "rights": [
            "info:eu-repo/semantics/embargoedAccess",
            "A custom license",
            "https://customlicense.org/licenses/by/4.0/",
            "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0/legalcode",
        ],
    }

    serializer = DublinCoreJSONSerializer()
    serialized_record = serializer.dump_one(updated_full_record)

    assert serialized_record == expected_data


def test_dublincorejson_serializer_minimal(running_app, updated_minimal_record):
    """Test serializer to Dublin Core JSON with minimal record"""
    expected_data = {
        "types": ["info:eu-repo/semantic/other"],
        "titles": ["A Romans story"],
        "creators": ["Name", "Troy Inc."],
        "dates": ["2020-06-01"],
        "rights": ["info:eu-repo/semantics/openAccess"],
        "publishers": ["Acme Inc"],
    }

    serializer = DublinCoreJSONSerializer()
    serialized_record = serializer.dump_one(updated_minimal_record)

    assert serialized_record == expected_data


def test_vocabulary_type_error(running_app, updated_minimal_record):
    """Test error thrown on missing resource type."""
    updated_minimal_record["metadata"]["resource_type"]["id"] = "invalid"

    with pytest.raises(VocabularyItemNotFoundError):
        DublinCoreJSONSerializer().dump_one(updated_minimal_record)


def test_dublincorexml_serializer(running_app, updated_full_record):
    """Test serializer to Dublin Core XML"""
    expected_data = [
        "<dc:contributor>Nielsen, Lars Holm</dc:contributor>",
        "<dc:creator>Nielsen, Lars Holm</dc:creator>",
        "<dc:date>2018/2020-09</dc:date>",
        "<dc:date>info:eu-repo/date/embargoEnd/2131-01-01</dc:date>",
        "<dc:description>A description \nwith HTML tags</dc:description>",
        "<dc:description>Bla bla bla</dc:description>",
        "<dc:format>application/pdf</dc:format>",
        "<dc:identifier>1924MNRAS..84..308E</dc:identifier>",
        "<dc:identifier>10.5281/inveniordm.1234</dc:identifier>",
        "<dc:language>dan</dc:language>",
        "<dc:language>eng</dc:language>",
        "<dc:publisher>InvenioRDM</dc:publisher>",
        "<dc:relation>doi:10.1234/foo.bar</dc:relation>",
        "<dc:rights>info:eu-repo/semantics/embargoedAccess</dc:rights>",
        "<dc:rights>A custom license</dc:rights>",
        "<dc:rights>https://customlicense.org/licenses/by/4.0/</dc:rights>",
        "<dc:rights>Creative Commons Attribution 4.0 " + "International</dc:rights>",
        "<dc:rights>https://creativecommons.org/licenses/by/4.0/legalcode"
        + "</dc:rights>",
        "<dc:title>InvenioRDM</dc:title>",
        "<dc:type>info:eu-repo/semantic/other</dc:type>",
    ]

    serializer = DublinCoreXMLSerializer()
    serialized_record = serializer.serialize_object(updated_full_record)

    for ed in expected_data:
        assert ed in serialized_record


def test_dublincorexml_serializer_minimal(running_app, updated_minimal_record):
    """Test serializer to Dublin Core XML with minimal record."""
    expected_data = [
        "<dc:creator>Name</dc:creator>",
        "<dc:creator>Troy Inc.</dc:creator>",
        "<dc:date>2020-06-01</dc:date>",
        "<dc:rights>info:eu-repo/semantics/openAccess</dc:rights>",
        "<dc:title>A Romans story</dc:title>",
        "<dc:type>info:eu-repo/semantic/other</dc:type>",
    ]

    serializer = DublinCoreXMLSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    for ed in expected_data:
        assert ed in serialized_record


def test_dublincorexml_serializer_list(
    running_app, updated_full_record, updated_minimal_record
):
    expected_data_full = [
        "<dc:contributor>Nielsen, Lars Holm</dc:contributor>",
        "<dc:creator>Nielsen, Lars Holm</dc:creator>",
        "<dc:date>2018/2020-09</dc:date>",
        "<dc:date>info:eu-repo/date/embargoEnd/2131-01-01</dc:date>",
        "<dc:description>A description \nwith HTML tags</dc:description>",
        "<dc:description>Bla bla bla</dc:description>",
        "<dc:format>application/pdf</dc:format>",
        "<dc:identifier>1924MNRAS..84..308E</dc:identifier>",
        "<dc:identifier>10.5281/inveniordm.1234</dc:identifier>",
        "<dc:language>dan</dc:language>",
        "<dc:language>eng</dc:language>",
        "<dc:publisher>InvenioRDM</dc:publisher>",
        "<dc:relation>doi:10.1234/foo.bar</dc:relation>",
        "<dc:rights>info:eu-repo/semantics/embargoedAccess</dc:rights>",
        "<dc:rights>A custom license</dc:rights>",
        "<dc:rights>https://customlicense.org/licenses/by/4.0/</dc:rights>",
        "<dc:rights>Creative Commons Attribution 4.0 " + "International</dc:rights>",
        "<dc:rights>https://creativecommons.org/licenses/by/4.0/legalcode"
        + "</dc:rights>",
        "<dc:title>InvenioRDM</dc:title>",
        "<dc:type>info:eu-repo/semantic/other</dc:type>",
    ]

    expected_data_minimal = [
        "<dc:creator>Name</dc:creator>",
        "<dc:creator>Troy Inc.</dc:creator>",
        "<dc:date>2020-06-01</dc:date>",
        "<dc:rights>info:eu-repo/semantics/openAccess</dc:rights>",
        "<dc:title>A Romans story</dc:title>",
        "<dc:type>info:eu-repo/semantic/other</dc:type>",
    ]

    serializer = DublinCoreXMLSerializer()
    serialized_records = serializer.serialize_object_list(
        {"hits": {"hits": [updated_full_record, updated_minimal_record]}}
    )

    for ed in expected_data_full:
        assert ed in serialized_records

    for ed in expected_data_minimal:
        assert ed in serialized_records
