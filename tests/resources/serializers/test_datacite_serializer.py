# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021-2024 Caltech.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers import (
    DataCite43JSONSerializer,
    DataCite43XMLSerializer,
)


@pytest.fixture(scope="function")
def minimal_record(minimal_record, parent_record):
    """Minimal record metadata with added parent metadata."""
    minimal_record["parent"] = parent_record
    minimal_record["links"] = dict(self_html="https://self-link.com")
    return minimal_record


@pytest.fixture
def full_modified_record(full_record_to_dict):
    full_record_to_dict["pids"]["unknown-scheme"] = {
        "identifier": "unknown-1234",
        "provider": "unknown",
        "client": "unknown",
    }

    full_record_to_dict["metadata"]["identifiers"] = [
        {"identifier": "unknown-1234-a", "scheme": "unknown-scheme"}
    ]

    full_record_to_dict["metadata"]["related_identifiers"] = [
        {
            "identifier": "unknown-1234-b",
            "scheme": "unknown-scheme",
            "relation_type": {"id": "iscitedby", "title": {"en": "Is cited by"}},
        }
    ]

    full_record_to_dict["metadata"]["creators"][0]["person_or_org"]["identifiers"] = [
        {"identifier": "unknown-2345", "scheme": "unknown-scheme"}
    ]

    return full_record_to_dict


@pytest.fixture
def full_geolocation_box_record(full_record_to_dict):
    full_record_to_dict["metadata"]["locations"]["features"] = [
        {
            "geometry": {
                "coordinates": [
                    [
                        [-105.92, 33.17],
                        [-106.0, 33.17],
                        [-106.0, 33.0],
                        [-105.92, 33.0],
                        [-105.92, 33.17],
                    ]
                ],
                "type": "Polygon",
            }
        }
    ]
    return full_record_to_dict


@pytest.fixture
def full_geolocation_polygon_record(full_record_to_dict):
    full_record_to_dict["metadata"]["locations"]["features"] = [
        {
            "geometry": {
                "coordinates": [
                    [
                        [33.17, -105.92],
                        [33.17, -106.0],
                        [33.0, -106.0],
                        [33.0, -105.92],
                        [33.12, -105.92],
                        [33.17, -105.32],
                    ]
                ],
                "type": "Polygon",
            }
        }
    ]
    return full_record_to_dict


@pytest.fixture
def full_modified_date_record(full_record_to_dict):
    full_record_to_dict["updated"] = "2022-12-12T22:50:10.573125+00:00"
    return full_record_to_dict


def test_datacite43_serializer(running_app, full_record_to_dict):
    """Test serializer to DataCite 4.3 JSON"""
    full_record_to_dict["metadata"]["rights"].append(
        {
            "title": {"en": "No rightsUri license"},
        }
    )
    # for HTML stripping test purposes
    expected_data = {
        "contributors": [
            {
                "affiliation": [{"name": "CERN"}, {"name": "TU Wien"}],
                "contributorType": "Other",
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "name": "Nielsen, Lars Holm",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0000-0001-8135-3489",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
                "nameType": "Personal",
            },
            {
                "contributorType": "Other",
                "familyName": "Dirk",
                "givenName": "Dirkin",
                "name": "Dirk, Dirkin",
                "nameIdentifiers": [],
                "nameType": "Personal",
            },
        ],
        "creators": [
            {
                "affiliation": [{"name": "CERN"}, {"name": "free-text"}],
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "name": "Nielsen, Lars Holm",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0000-0001-8135-3489",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
                "nameType": "Personal",
            },
            {
                "familyName": "Tom",
                "givenName": "Blabin",
                "name": "Tom, Blabin",
                "nameIdentifiers": [],
                "nameType": "Personal",
            },
        ],
        "dates": [
            {"date": "2018/2020-09", "dateType": "Issued"},
            {"date": "1939/1945", "dateInformation": "A date", "dateType": "Other"},
            {"date": "2023-11-14", "dateType": "Updated"},
        ],
        "descriptions": [
            {
                "description": "A description \nwith HTML tags",
                "descriptionType": "Abstract",
            },
            {"description": "Bla bla bla", "descriptionType": "Methods", "lang": "eng"},
        ],
        "formats": ["application/pdf"],
        "fundingReferences": [
            {
                "awardNumber": "111023",
                "awardTitle": "Launching of the research program on "
                "meaning processing",
                "awardURI": "https://sandbox.zenodo.org/",
                "funderName": "European Commission",
            }
        ],
        "geoLocations": [
            {
                "geoLocationPlace": "test location place",
                "geoLocationPoint": {
                    "pointLatitude": "-60.63932",
                    "pointLongitude": "-32.94682",
                },
            }
        ],
        "identifiers": [
            {
                "identifier": "https://127.0.0.1:5000/records/12345-abcde",
                "identifierType": "URL",
            },
            {"identifier": "10.1234/12345-abcde", "identifierType": "DOI"},
            {"identifier": "oai:invenio-rdm.com:12345-abcde", "identifierType": "oai"},
            {"identifier": "1924MNRAS..84..308E", "identifierType": "bibcode"},
        ],
        "language": "dan",
        "publicationYear": "2018",
        "publisher": "InvenioRDM",
        "relatedIdentifiers": [
            {
                "relatedIdentifier": "10.1234/foo.bar",
                "relatedIdentifierType": "DOI",
                "relationType": "IsCitedBy",
                "resourceTypeGeneral": "Dataset",
            },
            {
                "relatedIdentifier": "10.1234/pgfpj-at058",
                "relatedIdentifierType": "DOI",
                "relationType": "IsVersionOf",
            },
        ],
        "rightsList": [
            {
                "rights": "A custom license",
                "rightsUri": "https://customlicense.org/licenses/by/4.0/",
            },
            {
                "rights": "Creative Commons Attribution 4.0 International",
                "rightsIdentifier": "cc-by-4.0",
                "rightsIdentifierScheme": "spdx",
                "rightsUri": "https://creativecommons.org/licenses/by/4.0/legalcode",
            },
            {"rights": "No rightsUri license"},
        ],
        "schemaVersion": "http://datacite.org/schema/kernel-4",
        "sizes": ["11 pages"],
        "subjects": [
            {
                "subject": "Abdominal Injuries",
                "subjectScheme": "MeSH",
                "valueURI": "http://id.nlm.nih.gov/mesh/A-D000007",
            },
            {"subject": "custom"},
        ],
        "titles": [
            {"title": "InvenioRDM"},
            {
                "lang": "eng",
                "title": "a research data management platform",
                "titleType": "Subtitle",
            },
        ],
        "types": {"resourceType": "Photo", "resourceTypeGeneral": "Image"},
        "version": "v1.0",
    }

    serializer = DataCite43JSONSerializer()
    serialized_record = serializer.dump_obj(full_record_to_dict)

    assert serialized_record == expected_data


def test_datacite43_xml_serializer(running_app, full_record_to_dict):
    expected_data = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<resource xmlns="http://datacite.org/schema/kernel-4" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://datacite.org/schema/kernel-4 '
        'http://schema.datacite.org/meta/kernel-4.3/metadata.xsd">\n'
        '  <identifier identifierType="DOI">10.1234/12345-abcde</identifier>\n'
        "  <alternateIdentifiers>\n"
        "    <alternateIdentifier "
        'alternateIdentifierType="URL">https://127.0.0.1:5000/records/12345-abcde</alternateIdentifier>\n'
        "    <alternateIdentifier "
        'alternateIdentifierType="oai">oai:invenio-rdm.com:12345-abcde</alternateIdentifier>\n'
        "    <alternateIdentifier "
        'alternateIdentifierType="bibcode">1924MNRAS..84..308E</alternateIdentifier>\n'
        "  </alternateIdentifiers>\n"
        "  <creators>\n"
        "    <creator>\n"
        '      <creatorName nameType="Personal">Nielsen, Lars Holm</creatorName>\n'
        "      <givenName>Lars Holm</givenName>\n"
        "      <familyName>Nielsen</familyName>\n"
        "      <nameIdentifier "
        'nameIdentifierScheme="ORCID">0000-0001-8135-3489</nameIdentifier>\n'
        "      <affiliation>CERN</affiliation>\n"
        "      <affiliation>free-text</affiliation>\n"
        "    </creator>\n"
        "    <creator>\n"
        '      <creatorName nameType="Personal">Tom, Blabin</creatorName>\n'
        "      <givenName>Blabin</givenName>\n"
        "      <familyName>Tom</familyName>\n"
        "    </creator>\n"
        "  </creators>\n"
        "  <titles>\n"
        "    <title>InvenioRDM</title>\n"
        '    <title xml:lang="eng" titleType="Subtitle">a research data management '
        "platform</title>\n"
        "  </titles>\n"
        "  <publisher>InvenioRDM</publisher>\n"
        "  <publicationYear>2018</publicationYear>\n"
        "  <subjects>\n"
        '    <subject subjectScheme="MeSH">Abdominal Injuries</subject>\n'
        "    <subject>custom</subject>\n"
        "  </subjects>\n"
        "  <contributors>\n"
        '    <contributor contributorType="Other">\n'
        '      <contributorName nameType="Personal">Nielsen, Lars '
        "Holm</contributorName>\n"
        "      <givenName>Lars Holm</givenName>\n"
        "      <familyName>Nielsen</familyName>\n"
        "      <nameIdentifier "
        'nameIdentifierScheme="ORCID">0000-0001-8135-3489</nameIdentifier>\n'
        "      <affiliation>CERN</affiliation>\n"
        "      <affiliation>TU Wien</affiliation>\n"
        "    </contributor>\n"
        '    <contributor contributorType="Other">\n'
        '      <contributorName nameType="Personal">Dirk, Dirkin</contributorName>\n'
        "      <givenName>Dirkin</givenName>\n"
        "      <familyName>Dirk</familyName>\n"
        "    </contributor>\n"
        "  </contributors>\n"
        "  <dates>\n"
        '    <date dateType="Issued">2018/2020-09</date>\n'
        '    <date dateType="Other" dateInformation="A date">1939/1945</date>\n'
        '    <date dateType="Updated">2023-11-14</date>\n'
        "  </dates>\n"
        "  <language>dan</language>\n"
        '  <resourceType resourceTypeGeneral="Image">Photo</resourceType>\n'
        "  <relatedIdentifiers>\n"
        '    <relatedIdentifier relatedIdentifierType="DOI" relationType="IsCitedBy" '
        'resourceTypeGeneral="Dataset">10.1234/foo.bar</relatedIdentifier>\n'
        '    <relatedIdentifier relatedIdentifierType="DOI" '
        'relationType="IsVersionOf">10.1234/pgfpj-at058</relatedIdentifier>\n'
        "  </relatedIdentifiers>\n"
        "  <sizes>\n"
        "    <size>11 pages</size>\n"
        "  </sizes>\n"
        "  <formats>\n"
        "    <format>application/pdf</format>\n"
        "  </formats>\n"
        "  <version>v1.0</version>\n"
        "  <rightsList>\n"
        '    <rights rightsURI="https://customlicense.org/licenses/by/4.0/">A custom '
        "license</rights>\n"
        "    <rights "
        'rightsURI="https://creativecommons.org/licenses/by/4.0/legalcode" '
        'rightsIdentifierScheme="spdx" rightsIdentifier="cc-by-4.0">Creative Commons '
        "Attribution 4.0 International</rights>\n"
        "  </rightsList>\n"
        "  <descriptions>\n"
        '    <description descriptionType="Abstract">A description \n'
        "with HTML tags</description>\n"
        '    <description descriptionType="Methods" xml:lang="eng">Bla bla '
        "bla</description>\n"
        "  </descriptions>\n"
        "  <geoLocations>\n"
        "    <geoLocation>\n"
        "      <geoLocationPlace>test location place</geoLocationPlace>\n"
        "      <geoLocationPoint>\n"
        "        <pointLongitude>-32.94682</pointLongitude>\n"
        "        <pointLatitude>-60.63932</pointLatitude>\n"
        "      </geoLocationPoint>\n"
        "    </geoLocation>\n"
        "  </geoLocations>\n"
        "  <fundingReferences>\n"
        "    <fundingReference>\n"
        "      <funderName>European Commission</funderName>\n"
        "      <awardNumber>111023</awardNumber>\n"
        "      <awardTitle>Launching of the research program on meaning "
        "processing</awardTitle>\n"
        "    </fundingReference>\n"
        "  </fundingReferences>\n"
        "</resource>\n"
    )

    serializer = DataCite43XMLSerializer()
    serialized_record = serializer.serialize_object(full_record_to_dict)

    assert serialized_record == expected_data


def test_datacite43_identifiers(running_app, minimal_record):
    """Test serialization of records with DOI alternate identifiers"""
    # Mimic user putting DOI in alternate identifier field
    minimal_record["metadata"]["identifiers"] = [
        {"identifier": "10.1234/inveniordm.1234", "scheme": "doi"}
    ]

    serializer = DataCite43JSONSerializer()
    serialized_record = serializer.dump_obj(minimal_record)

    assert len(serialized_record["identifiers"]) == 1

    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.1234/inveniordm.1234",
            "provider": "datacite",
            "client": "inveniordm",
        }
    }

    serialized_record = serializer.dump_obj(minimal_record)
    assert len(serialized_record["identifiers"]) == 2
    identifier = serialized_record["identifiers"][0]["identifier"]
    assert identifier == "https://self-link.com"
    identifier = serialized_record["identifiers"][1]["identifier"]
    assert identifier == "10.1234/inveniordm.1234"


def test_datacite43_serializer_with_unknown_id_schemes(
    running_app, full_modified_record
):
    """Test if the DataCite 4.3 JSON serializer can handle unknown schemes."""
    # this test is there to ensure that there are no KeyErrors during the
    # lookup of unknown PID schemes during DataCite 4.3 serialization
    # if the behaviour of the datacite serializer is changed, the asserts
    # below should probably be adjusted accordingly

    expected_pid_id = {"identifier": "unknown-1234", "identifierType": "unknown-scheme"}
    expected_pid_id_2 = {
        "identifier": "unknown-1234-a",
        "identifierType": "unknown-scheme",
    }
    expected_related_id = {
        "relatedIdentifier": "unknown-1234-b",
        "relatedIdentifierType": "unknown-scheme",
        "relationType": "IsCitedBy",
    }
    expected_creator_id = {
        "nameIdentifier": "unknown-2345",
        "nameIdentifierScheme": "unknown-scheme",
    }

    serializer = DataCite43JSONSerializer()
    serialized_record = serializer.dump_obj(full_modified_record)

    assert expected_pid_id in serialized_record["identifiers"]
    assert expected_pid_id_2 in serialized_record["identifiers"]
    assert len(serialized_record["identifiers"]) == 5

    assert expected_related_id not in serialized_record["relatedIdentifiers"]
    assert len(serialized_record["relatedIdentifiers"]) == 1

    creator_ids = serialized_record["creators"][0]["nameIdentifiers"]
    assert expected_creator_id in creator_ids
    assert len(creator_ids) == 1


def test_datacite43_xml_serializer_with_unknown_id_schemes(
    running_app, full_modified_record
):
    """Test if the DataCite 4.3 XML serializer can handle unknown schemes."""
    serializer = DataCite43XMLSerializer()
    serialized_record = serializer.serialize_object(full_modified_record)
    expected_pid_id = '<alternateIdentifier alternateIdentifierType="unknown-scheme">unknown-1234</alternateIdentifier>'  # noqa
    expected_pid_id_2 = '<alternateIdentifier alternateIdentifierType="unknown-scheme">unknown-1234-a</alternateIdentifier>'  # noqa
    expected_related_id = '<relatedIdentifier relatedIdentifierType="unknown-scheme" relationType="IsCitedBy">unknown-1234-b</relatedIdentifier>'  # noqa
    expected_creator_id = '<nameIdentifier nameIdentifierScheme="unknown-scheme">unknown-2345</nameIdentifier>'  # noqa

    assert expected_pid_id in serialized_record
    assert expected_pid_id_2 in serialized_record
    assert expected_related_id not in serialized_record
    assert expected_creator_id in serialized_record


def test_datacite43_serializer_with_box(running_app, full_geolocation_box_record):
    """Test if the DataCite 4.3 JSON serializer handles geolocation boxes."""

    expected_box = {
        "geoLocationBox": {
            "eastBoundLongitude": "-105.92",
            "northBoundLatitude": "33.17",
            "southBoundLatitude": "33.0",
            "westBoundLongitude": "-106.0",
        }
    }

    serializer = DataCite43JSONSerializer()

    serialized_record_box = serializer.dump_obj(full_geolocation_box_record)

    assert expected_box in serialized_record_box["geoLocations"]


def test_datacite43_serializer_with_polygon(
    running_app, full_geolocation_polygon_record
):
    """Test if the DataCite 4.3 JSON serializer handles geolocation polygons."""

    expected_polygon = {
        "geoLocationPolygon": [
            {"polygonPoint": {"pointLongitude": "33.17", "pointLatitude": "-105.92"}},
            {"polygonPoint": {"pointLongitude": "33.17", "pointLatitude": "-106.0"}},
            {"polygonPoint": {"pointLongitude": "33.0", "pointLatitude": "-106.0"}},
            {"polygonPoint": {"pointLongitude": "33.0", "pointLatitude": "-105.92"}},
            {"polygonPoint": {"pointLongitude": "33.12", "pointLatitude": "-105.92"}},
            {"polygonPoint": {"pointLongitude": "33.17", "pointLatitude": "-105.32"}},
        ]
    }

    serializer = DataCite43JSONSerializer()

    serialized_record_polygon = serializer.dump_obj(full_geolocation_polygon_record)

    assert expected_polygon in serialized_record_polygon["geoLocations"]


def test_datacite43_serializer_updated_date(running_app, full_modified_date_record):
    """Test if the DataCite 4.3 JSON serializer adds system updated date."""

    expected_dates = [
        {"date": "2018/2020-09", "dateType": "Issued"},
        {"date": "1939/1945", "dateType": "Other", "dateInformation": "A date"},
        {"date": "2022-12-12", "dateType": "Updated"},
    ]

    serializer = DataCite43JSONSerializer()
    serialized_record = serializer.dump_obj(full_modified_date_record)

    assert expected_dates == serialized_record["dates"]
    assert len(serialized_record["dates"]) == 3


def test_datacite43_serializer_empty_record(running_app, empty_record):
    """Test if the DataCite 4.3 JSON serializer handles an empty record."""

    expected_data = {"schemaVersion": "http://datacite.org/schema/kernel-4"}

    serializer = DataCite43JSONSerializer()
    serialized_record = serializer.dump_obj(empty_record)

    assert serialized_record == expected_data
