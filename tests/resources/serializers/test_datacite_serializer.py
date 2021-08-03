
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Caltech.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_rdm_records.resources.serializers import \
    DataCite43JSONSerializer, DataCite43XMLSerializer


@pytest.fixture(scope="function")
def resource_type_v(resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(system_identity, {  # create base resource type
        "id": "image",
        "icon": "chart bar outline",
        "props": {
            "csl": "figure",
            "datacite_general": "Image",
            "datacite_type": "",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/ImageObject",
            "subtype": "",
            "type": "image",
        },
        "title": {
            "en": "Image"
        },
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes"
    })

    vocabulary_service.create(system_identity, {
        "id": "image-photo",
        "icon": "chart bar outline",
        "props": {
            "csl": "graphic",
            "datacite_general": "Image",
            "datacite_type": "Photo",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/Photograph",
            "subtype": "image-photo",
            "type": "image",
        },
        "title": {
            "en": "Photo"
        },
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes"
    })

    vocab = vocabulary_service.create(system_identity, {
        "id": "dataset",
        "icon": "table",
        "props": {
            "csl": "dataset",
            "datacite_general": "Dataset",
            "datacite_type": '',
            "openaire_resourceType": '21',
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/Dataset",
            "subtype": '',
            "type": "dataset",
        },
        "title": {
            "en": "Dataset"
        },
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="function")
def title_type_v(app, title_type):
    """Title Type vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "subtitle",
        "props": {
            "datacite": "Subtitle"
        },
        "title": {
            "en": "Subtitle"
        },
        "type": "titletypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture
def running_app(
    app, location, resource_type_v, subject_v, languages_v, title_type_v,
    description_type_v, affiliations_v, date_type_v, contributors_role_v,
    relation_type_v, licenses_v
):
    """Return running_app but load everything for datacite serialization.

    Since test_datacite43_serializer doesn't use content of running_app, we
    don't bother with a new namedtuple.
    """
    return running_app


def test_datacite43_serializer(running_app, full_record):
    """Test serializer to DataCite 4.3 JSON"""
    full_record["metadata"]["rights"].append(
        {
            "title": {
                "en": "No rightsUri license"
            },
        }
    )
    # for HTML stripping test purposes
    expected_data = {
        "types": {
            "resourceTypeGeneral": "Image",
            "resourceType": "Photo"
        },
        "creators": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [{
                    "nameIdentifier": "0000-0001-8135-3489",
                    "nameIdentifierScheme": "ORCID",
                }],
                "affiliation": [
                    {'name': 'free-text'},
                    {
                        "name": "CERN",
                        "affiliationIdentifier": "01ggx4157",
                        "affiliationIdentifierScheme": "ROR",
                    }
                ],
            }
        ],
        "titles": [
            {"title": "InvenioRDM"},
            {
                "title": "a research data management platform",
                "titleType": "Subtitle",
                "lang": "eng",
            },
        ],
        "publisher": "InvenioRDM",
        "publicationYear": "2018",
        "subjects": [{
            "subject": "custom"
        }, {
            "subject": "Abdominal Injuries",
            "subjectScheme": "MeSH",
            "valueURI": "http://id.nlm.nih.gov/mesh/A-D000007",
        }],
        "contributors": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "contributorType": "Other",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [{
                    "nameIdentifier": "0000-0001-8135-3489",
                    "nameIdentifierScheme": "ORCID",
                }],
                "affiliation": [
                    {
                        "name": "CERN",
                        "affiliationIdentifier": "01ggx4157",
                        "affiliationIdentifierScheme": "ROR",
                    }
                ],
            }
        ],
        "dates": [
            {"date": "2018/2020-09", "dateType": "Issued"},
            {
                "date": "1939/1945",
                "dateType": "Other",
                "dateInformation": "A date"
            },
        ],
        "language": "dan",
        "identifiers": [
            {
                "identifier": "10.5281/inveniordm.1234",
                "identifierType": "DOI"
            },
            {
                "identifier": "1924MNRAS..84..308E",
                "identifierType": "bibcode"
            },
        ],
        "relatedIdentifiers": [
            {
                "relatedIdentifier": "10.1234/foo.bar",
                "relatedIdentifierType": "DOI",
                "relationType": "IsCitedBy",
                "resourceTypeGeneral": "Dataset",
            }
        ],
        "sizes": ["11 pages"],
        "formats": ["application/pdf"],
        "version": "v1.0",
        "rightsList": [
            {
                'rights': 'A custom license',
                'rightsUri': 'https://customlicense.org/licenses/by/4.0/'
            },
            {
                'rights': 'No rightsUri license'
            },
            {
                "rights": "Creative Commons Attribution 4.0 International",
                "rightsIdentifierScheme": "spdx",
                "rightsIdentifier": "cc-by-4.0",
                "rightsUri": "https://creativecommons.org/licenses/by/4.0/"
                             "legalcode",
            },
        ],
        "descriptions": [
            {
                "description": "A description with HTML tags",
                "descriptionType": "Abstract"
            }, {
                "description": "Bla bla bla",
                "descriptionType": "Methods",
                "lang": "eng"
            },
        ],
        "geoLocations": [
            {
                "geoLocationPoint": {
                    'pointLatitude': -32.94682,
                    'pointLongitude': -60.63932
                },
                "geoLocationPlace": "test location place",
            }
        ],
        "fundingReferences": [
            {
                "funderName": "European Commission",
                "funderIdentifier": "1234",
                "funderIdentifierType": "ROR",
                "awardTitle": "OpenAIRE",
                "awardNumber": "246686",
                "awardURI": ".../246686",
            }
        ],
        "schemaVersion": "http://datacite.org/schema/kernel-4",
    }

    serializer = DataCite43JSONSerializer()
    serialized_record = serializer.dump_one(full_record)

    assert serialized_record == expected_data


def test_datacite43_xml_serializer(running_app, full_record):
    expected_data = [
        "<?xml version='1.0' encoding='utf-8'?>",
        "<resource xmlns=\"http://datacite.org/schema/kernel-4\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.3/metadata.xsd\">",  # noqa
        "  <identifier identifierType=\"DOI\">10.5281/inveniordm.1234</identifier>",  # noqa
        "  <alternateIdentifiers>",
        "    <alternateIdentifier alternateIdentifierType=\"bibcode\">1924MNRAS..84..308E</alternateIdentifier>",  # noqa
        "  </alternateIdentifiers>",
        "  <creators>",
        "    <creator>",
        "      <creatorName nameType=\"Personal\">Nielsen, Lars Holm</creatorName>",  # noqa
        "      <givenName>Lars Holm</givenName>",
        "      <familyName>Nielsen</familyName>",
        "      <nameIdentifier nameIdentifierScheme=\"ORCID\">0000-0001-8135-3489</nameIdentifier>",  # noqa
        "      <affiliation>free-text</affiliation>",
        "      <affiliation affiliationIdentifier=\"01ggx4157\" affiliationIdentifierScheme=\"ROR\">CERN</affiliation>",  # noqa
        "    </creator>",
        "  </creators>",
        "  <titles>",
        "    <title>InvenioRDM</title>",
        "    <title xml:lang=\"eng\" titleType=\"Subtitle\">a research data management platform</title>",  # noqa
        "  </titles>",
        "  <publisher>InvenioRDM</publisher>",
        "  <publicationYear>2018</publicationYear>",
        "  <subjects>",
        "    <subject>custom</subject>",
        "    <subject subjectScheme=\"MeSH\">Abdominal Injuries</subject>",
        "  </subjects>",
        "  <contributors>",
        "    <contributor contributorType=\"Other\">",
        "      <contributorName nameType=\"Personal\">Nielsen, Lars Holm</contributorName>",  # noqa
        "      <givenName>Lars Holm</givenName>",
        "      <familyName>Nielsen</familyName>",
        "      <nameIdentifier nameIdentifierScheme=\"ORCID\">0000-0001-8135-3489</nameIdentifier>",  # noqa
        "      <affiliation affiliationIdentifier=\"01ggx4157\" affiliationIdentifierScheme=\"ROR\">CERN</affiliation>",  # noqa
        "    </contributor>",
        "  </contributors>",
        "  <dates>",
        "    <date dateType=\"Issued\">2018/2020-09</date>",
        "    <date dateType=\"Other\" dateInformation=\"A date\">1939/1945</date>",  # noqa
        "  </dates>",
        "  <language>dan</language>",
        "  <resourceType resourceTypeGeneral=\"Image\">Photo</resourceType>",
        "  <relatedIdentifiers>",
        "    <relatedIdentifier relatedIdentifierType=\"DOI\" relationType=\"IsCitedBy\" resourceTypeGeneral=\"Dataset\">10.1234/foo.bar</relatedIdentifier>",  # noqa
        "  </relatedIdentifiers>",
        "  <sizes>",
        "    <size>11 pages</size>",
        "  </sizes>",
        "  <formats>",
        "    <format>application/pdf</format>",
        "  </formats>",
        "  <version>v1.0</version>",
        "  <rightsList>",
        "    <rights rightsURI=\"https://customlicense.org/licenses/by/4.0/\">A custom license</rights>",  # noqa
        "    <rights rightsURI=\"https://creativecommons.org/licenses/by/4.0/legalcode\" rightsIdentifierScheme=\"spdx\" rightsIdentifier=\"cc-by-4.0\">Creative Commons Attribution 4.0 International</rights>",  # noqa
        "  </rightsList>",
        "  <descriptions>",
        "    <description descriptionType=\"Abstract\">A description with HTML tags</description>",  # noqa
        "    <description descriptionType=\"Methods\" xml:lang=\"eng\">Bla bla bla</description>",  # noqa
        "  </descriptions>",
        "  <geoLocations>",
        "    <geoLocation>",
        "      <geoLocationPlace>test location place</geoLocationPlace>",
        "      <geoLocationPoint>",
        "        <pointLongitude>-60.63932</pointLongitude>",
        "        <pointLatitude>-32.94682</pointLatitude>",
        "      </geoLocationPoint>",
        "    </geoLocation>",
        "  </geoLocations>",
        "  <fundingReferences>",
        "    <fundingReference>",
        "      <funderName>European Commission</funderName>",
        "      <funderIdentifier funderIdentifierType=\"ROR\">1234</funderIdentifier>",  # noqa
        "      <awardNumber>246686</awardNumber>",
        "      <awardTitle>OpenAIRE</awardTitle>",
        "    </fundingReference>",
        "  </fundingReferences>",
        "</resource>",
        ""  # this is because of the split
    ]

    serializer = DataCite43XMLSerializer()
    serialized_record = serializer.serialize_object(full_record)

    # split by breaklines makes it easier to see diffs
    assert serialized_record.split("\n") == expected_data
