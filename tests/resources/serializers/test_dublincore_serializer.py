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
def updated_minimal_record(minimal_record):
    """Update fields (done after record create) for Dublin Core serializer."""
    minimal_record["access"]["status"] = "open"
    minimal_record["parent"] = dict()
    for creator in minimal_record["metadata"]["creators"]:
        name = creator["person_or_org"].get("name")
        if not name:
            creator["person_or_org"]["name"] = "Name"

    return minimal_record


def test_dublincorejson_serializer(running_app, full_record_to_dict):
    """Test serializer to Dublin Core JSON"""
    expected_data = {
        "contributors": ["Nielsen, Lars Holm", "Dirk, Dirkin"],
        "creators": ["Nielsen, Lars Holm", "Tom, Blabin"],
        "dates": ["2018/2020-09", "info:eu-repo/date/embargoEnd/2131-01-01"],
        "descriptions": [
            "&lt;h1&gt;A description&lt;/h1&gt; &lt;p&gt;with HTML " "tags&lt;/p&gt;",
            "Bla bla bla",
        ],
        "formats": ["application/pdf"],
        "identifiers": [
            "https://doi.org/10.1234/12345-abcde",
            "oai:invenio-rdm.com:12345-abcde",
            "https://ui.adsabs.harvard.edu/#abs/1924MNRAS..84..308E",
        ],
        "languages": ["dan", "eng"],
        "locations": [
            "name=test location place; description=test location "
            "description; lat=-32.94682; lon=-60.63932"
        ],
        "publishers": ["InvenioRDM"],
        "relations": [
            "https://doi.org/10.1234/foo.bar",
            "https://doi.org/10.1234/pgfpj-at058",
        ],
        "rights": [
            "info:eu-repo/semantics/embargoedAccess",
            "A custom license",
            "https://customlicense.org/licenses/by/4.0/",
            "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0/legalcode",
        ],
        "subjects": ["Abdominal Injuries", "custom"],
        "titles": ["InvenioRDM"],
        "types": ["info:eu-repo/semantics/other"],
    }

    serializer = DublinCoreJSONSerializer()
    serialized_record = serializer.dump_obj(full_record_to_dict)

    assert serialized_record == expected_data


def test_dublincorejson_serializer_minimal(running_app, updated_minimal_record):
    """Test serializer to Dublin Core JSON with minimal record"""
    expected_data = {
        "types": ["info:eu-repo/semantics/other"],
        "titles": ["A Romans story"],
        "creators": ["Name", "Troy Inc."],
        "dates": ["2020-06-01"],
        "rights": ["info:eu-repo/semantics/openAccess"],
        "publishers": ["Acme Inc"],
    }

    serializer = DublinCoreJSONSerializer()
    serialized_record = serializer.dump_obj(updated_minimal_record)

    assert serialized_record == expected_data


def test_dublincorejson_serializer_empty_record(running_app, empty_record):
    """Test serializer to Dublin Core JSON with an empty record"""

    expected_data = {}

    serializer = DublinCoreJSONSerializer()
    serialized_record = serializer.dump_obj(empty_record)

    assert serialized_record == expected_data


def test_vocabulary_type_error(running_app, updated_minimal_record):
    """Test error thrown on missing resource type."""
    updated_minimal_record["metadata"]["resource_type"]["id"] = "invalid"

    with pytest.raises(VocabularyItemNotFoundError):
        DublinCoreJSONSerializer().dump_obj(updated_minimal_record)


def test_dublincorexml_serializer(running_app, full_record_to_dict):
    """Test serializer to Dublin Core XML"""
    expected_data = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ '
        'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n'
        "  <dc:contributor>Nielsen, Lars Holm</dc:contributor>\n"
        "  <dc:contributor>Dirk, Dirkin</dc:contributor>\n"
        "  <dc:creator>Nielsen, Lars Holm</dc:creator>\n"
        "  <dc:creator>Tom, Blabin</dc:creator>\n"
        "  <dc:date>2018/2020-09</dc:date>\n"
        "  <dc:date>info:eu-repo/date/embargoEnd/2131-01-01</dc:date>\n"
        "  <dc:description>&amp;lt;h1&amp;gt;A description&amp;lt;/h1&amp;gt; "
        "&amp;lt;p&amp;gt;with HTML tags&amp;lt;/p&amp;gt;</dc:description>\n"
        "  <dc:description>Bla bla bla</dc:description>\n"
        "  <dc:format>application/pdf</dc:format>\n"
        "  <dc:identifier>https://doi.org/10.1234/12345-abcde</dc:identifier>\n"
        "  <dc:identifier>oai:invenio-rdm.com:12345-abcde</dc:identifier>\n"
        "  "
        "<dc:identifier>https://ui.adsabs.harvard.edu/#abs/1924MNRAS..84..308E</dc:identifier>\n"
        "  <dc:language>dan</dc:language>\n"
        "  <dc:language>eng</dc:language>\n"
        "  <dc:publisher>InvenioRDM</dc:publisher>\n"
        "  <dc:relation>https://doi.org/10.1234/foo.bar</dc:relation>\n"
        "  <dc:relation>https://doi.org/10.1234/pgfpj-at058</dc:relation>\n"
        "  <dc:rights>info:eu-repo/semantics/embargoedAccess</dc:rights>\n"
        "  <dc:rights>A custom license</dc:rights>\n"
        "  <dc:rights>https://customlicense.org/licenses/by/4.0/</dc:rights>\n"
        "  <dc:rights>Creative Commons Attribution 4.0 International</dc:rights>\n"
        "  "
        "<dc:rights>https://creativecommons.org/licenses/by/4.0/legalcode</dc:rights>\n"
        "  <dc:subject>Abdominal Injuries</dc:subject>\n"
        "  <dc:subject>custom</dc:subject>\n"
        "  <dc:title>InvenioRDM</dc:title>\n"
        "  <dc:type>info:eu-repo/semantics/other</dc:type>\n"
        "</oai_dc:dc>\n"
    )

    serializer = DublinCoreXMLSerializer()
    serialized_record = serializer.serialize_object(full_record_to_dict)
    assert serialized_record == expected_data


def test_dublincorexml_serializer_minimal(running_app, updated_minimal_record):
    """Test serializer to Dublin Core XML with minimal record."""
    expected_data = [
        "<dc:creator>Name</dc:creator>",
        "<dc:creator>Troy Inc.</dc:creator>",
        "<dc:date>2020-06-01</dc:date>",
        "<dc:rights>info:eu-repo/semantics/openAccess</dc:rights>",
        "<dc:title>A Romans story</dc:title>",
        "<dc:type>info:eu-repo/semantics/other</dc:type>",
    ]

    serializer = DublinCoreXMLSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    for ed in expected_data:
        assert ed in serialized_record


def test_dublincorexml_serializer_list(
    running_app, full_record_to_dict, updated_minimal_record
):
    expected_data_full = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ '
        'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n'
        "  <dc:contributor>Nielsen, Lars Holm</dc:contributor>\n"
        "  <dc:contributor>Dirk, Dirkin</dc:contributor>\n"
        "  <dc:creator>Nielsen, Lars Holm</dc:creator>\n"
        "  <dc:creator>Tom, Blabin</dc:creator>\n"
        "  <dc:date>2018/2020-09</dc:date>\n"
        "  <dc:date>info:eu-repo/date/embargoEnd/2131-01-01</dc:date>\n"
        "  <dc:description>&amp;lt;h1&amp;gt;A description&amp;lt;/h1&amp;gt; "
        "&amp;lt;p&amp;gt;with HTML tags&amp;lt;/p&amp;gt;</dc:description>\n"
        "  <dc:description>Bla bla bla</dc:description>\n"
        "  <dc:format>application/pdf</dc:format>\n"
        "  <dc:identifier>https://doi.org/10.1234/12345-abcde</dc:identifier>\n"
        "  <dc:identifier>oai:invenio-rdm.com:12345-abcde</dc:identifier>\n"
        "  "
        "<dc:identifier>https://ui.adsabs.harvard.edu/#abs/1924MNRAS..84..308E</dc:identifier>\n"
        "  <dc:language>dan</dc:language>\n"
        "  <dc:language>eng</dc:language>\n"
        "  <dc:publisher>InvenioRDM</dc:publisher>\n"
        "  <dc:relation>https://doi.org/10.1234/foo.bar</dc:relation>\n"
        "  <dc:relation>https://doi.org/10.1234/pgfpj-at058</dc:relation>\n"
        "  <dc:rights>info:eu-repo/semantics/embargoedAccess</dc:rights>\n"
        "  <dc:rights>A custom license</dc:rights>\n"
        "  <dc:rights>https://customlicense.org/licenses/by/4.0/</dc:rights>\n"
        "  <dc:rights>Creative Commons Attribution 4.0 International</dc:rights>\n"
        "  "
        "<dc:rights>https://creativecommons.org/licenses/by/4.0/legalcode</dc:rights>\n"
        "  <dc:subject>Abdominal Injuries</dc:subject>\n"
        "  <dc:subject>custom</dc:subject>\n"
        "  <dc:title>InvenioRDM</dc:title>\n"
        "  <dc:type>info:eu-repo/semantics/other</dc:type>\n"
        "</oai_dc:dc>\n"
    )

    expected_data_minimal = [
        "<dc:creator>Name</dc:creator>",
        "<dc:creator>Troy Inc.</dc:creator>",
        "<dc:date>2020-06-01</dc:date>",
        "<dc:rights>info:eu-repo/semantics/openAccess</dc:rights>",
        "<dc:title>A Romans story</dc:title>",
        "<dc:type>info:eu-repo/semantics/other</dc:type>",
    ]

    serializer = DublinCoreXMLSerializer()
    serialized_records = serializer.serialize_object_list(
        {"hits": {"hits": [full_record_to_dict, updated_minimal_record]}}
    )

    for ed in expected_data_full:
        assert ed in serialized_records

    for ed in expected_data_minimal:
        assert ed in serialized_records
