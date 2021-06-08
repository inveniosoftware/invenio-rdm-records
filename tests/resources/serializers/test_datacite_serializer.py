
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
from invenio_vocabularies.proxies import current_service as vocabulary_service

from invenio_rdm_records.resources.serializers import DataCite43JSONSerializer


@pytest.fixture(scope="function")
def resource_type_dataset(resource_type_type):
    """Resource type vocabulary record."""
    return vocabulary_service.create(system_identity, {
        "id": "dataset",
        "props": {
            "csl": "dataset",
            "datacite_general": "Dataset",
            "datacite_type": '',
            "openaire_resourceType": '21',
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/Dataset",
            "subtype": '',
            "subtype_name": '',
            "type": "dataset",
            "type_icon": "table",
            "type_name": "Dataset",
        },
        "title": {
            "en": "Dataset"
        },
        "type": "resource_types"
    })


def test_datacite43_serializer(
    running_app, full_record, resource_type_dataset, laguanges_vocabulary,
    vocabulary_clear
):
    """Test serializer to DayaCide 4.3 JSON"""
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
                    "nameIdentifier": "http://orcid.org/0000-0001-8135-3489",
                    "nameIdentifierScheme": "ORCID",
                    'schemeURI': 'http://orcid.org/'
                }],
                "affiliations": [
                    {
                        "name": "CERN",
                        "affiliationIdentifier": "https://ror.org/01ggx4157",
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
                "lang": "en",
            },
        ],
        "publisher": "InvenioRDM",
        "publicationYear": "2018",
        "subjects": [{
            "subject": "test",
            "valueURI": "test",
            "subjectScheme": "dewey"
        }],
        "contributors": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "contributorType": "Other",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [{
                    "nameIdentifier": "http://orcid.org/0000-0001-8135-3489",
                    "nameIdentifierScheme": "ORCID",
                    'schemeURI': 'http://orcid.org/'
                }],
                "affiliations": [
                    {
                        "name": "CERN",
                        "affiliationIdentifier": "https://ror.org/01ggx4157",
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
        "language": "da",
        "identifiers": [
            {
                "identifier": "1924MNRAS..84..308E",
                "identifierType": "bibcode"
            },
            {
                "identifier": "10.5281/inveniordm.1234",
                "identifierType": "DOI"
            },
        ],
        "relatedIdentifiers": [
            {
                "relatedIdentifier": "10.1234/foo.bar",
                "relatedIdentifierType": "DOI",
                "relationType": "Cites",
                "resourceTypeGeneral": "Dataset",
            }
        ],
        "sizes": ["11 pages"],
        "formats": ["application/pdf"],
        "version": "v1.0",
        "rightsList": [
            {
                "rights": "Creative Commons Attribution 4.0 International",
                "rightsIdentifierScheme": "spdx",
                "rightsIdentifier": "cc-by-4.0",
                "rightsUri": "https://creativecommons.org/licenses/by/4.0/",
            }
        ],
        "descriptions": [
            {"description": "Test", "descriptionType": "Abstract"},
            {
                "description": "Bla bla bla",
                "descriptionType": "Methods",
                "lang": "en"
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
