# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import json

from invenio_rdm_records.resources.serializers import UIJSONSerializer


def test_datacite43_serializer(app, full_record):
    """Test serializer to DayaCide 4.3 JSON"""
    expected_data = {
        "types": {"resourceTypeGeneral": "Text", "resourceType": "publication-article"},
        "creators": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0000-0001-8135-3489",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
                "affiliation": [
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
                "lang": "eng",
            },
        ],
        "publisher": "InvenioRDM",
        "publicationYear": "2018",
        "subjects": [{"subject": "test", "valueURI": "test", "subjectScheme": "dewey"}],
        "contributors": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "contributorType": "Other",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0000-0001-8135-3489",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
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
            {"date": "1939/1945", "dateType": "Other", "dateInformation": "A date"},
        ],
        "language": "da",
        "identifiers": [
            {"identifier": "1924MNRAS..84..308E", "identifierType": "bibcode"},
            {"identifier": "10.5281/zenodo.1234", "identifierType": "DOI"},
        ],
        "relatedIdentifiers": [
            {
                "relatedIdentifier": "10.1234/foo.bar",
                "relatedIdentifierType": "DOI",
                "relationType": "Cites",
                "resourceTypeGeneralype": "dataset",
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
            {"description": "Bla bla bla", "descriptionType": "Methods", "lang": "eng"},
        ],
        "geoLocations": [
            {
                "geoLocationPoint": {"pointLatitude": "1", "pointLongitude": "2"},
                "geoLocationPlace": "home",
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


def test_ui_serializer(app, full_record):
    """Test UI serializer."""
    expected_data = {
        # 'access_right': {},
        "contributors": {
            "affiliations": [[1, "CERN"]],
            "contributors": [
                {
                    "affiliations": [[1, "CERN"]],
                    "family_name": "Nielsen",
                    "given_name": "Lars Holm",
                    "identifiers": {"orcid": "0000-0001-8135-3489"},
                    "name": "Nielsen, Lars Holm",
                    "role": "other",
                    "type": "personal",
                }
            ],
        },
        "creators": {
            "affiliations": [[1, "CERN"]],
            "creators": [
                {
                    "affiliations": [[1, "CERN"]],
                    "family_name": "Nielsen",
                    "given_name": "Lars Holm",
                    "identifiers": {"orcid": "0000-0001-8135-3489"},
                    "name": "Nielsen, Lars Holm",
                    "type": "personal",
                }
            ],
        },
        "publication_date_l10n_long": "January 2018 – September 2020",
        "publication_date_l10n_medium": "Jan 2018 – Sep 2020",
        "resource_type": "Journal article",
        "languages": [
            {"id": "da", "title_l10n": "Danish"},
            {"id": "en", "title_l10n": "English"},
        ],
        "description_stripped": "Test",
        "version": "v1.0",
    }

    with app.app_context():
        serialized_record = UIJSONSerializer().serialize_object_to_dict(full_record)

    assert serialized_record["ui"] == expected_data
    serialized_records = UIJSONSerializer().serialize_object_list(
        {"hits": {"hits": [full_record]}}
    )
    assert json.loads(serialized_records)["hits"]["hits"][0]["ui"] == expected_data
