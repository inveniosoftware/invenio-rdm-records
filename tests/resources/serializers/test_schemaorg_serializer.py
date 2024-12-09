# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2021 Caltech.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from invenio_rdm_records.resources.serializers.schemaorg import (
    SchemaorgJSONLDSerializer,
)


def test_schemaorg_serializer_full_record(running_app, full_record_to_dict):
    """Test Schemaorg JSON-LD serializer with full record."""

    expected_data = {
        "@context": "http://schema.org",
        "@id": "https://doi.org/10.1234/12345-abcde",
        "@type": "https://schema.org/Photograph",
        "author": [
            {
                "@id": "https://orcid.org/0000-0001-8135-3489",
                "@type": "Person",
                "affiliation": [
                    {"@type": "Organization", "name": "CERN"},
                    {"@type": "Organization", "name": "free-text"},
                ],
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "name": "Nielsen, Lars Holm",
            },
            {
                "@type": "Person",
                "familyName": "Tom",
                "givenName": "Blabin",
                "name": "Tom, Blabin",
            },
        ],
        "contentSize": "9.0 B",
        "creator": [
            {
                "@id": "https://orcid.org/0000-0001-8135-3489",
                "@type": "Person",
                "affiliation": [
                    {"@type": "Organization", "name": "CERN"},
                    {"@type": "Organization", "name": "free-text"},
                ],
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "name": "Nielsen, Lars Holm",
            },
            {
                "@type": "Person",
                "familyName": "Tom",
                "givenName": "Blabin",
                "name": "Tom, Blabin",
            },
        ],
        "datePublished": "2018",
        "description": "<h1>A description</h1> <p>with HTML tags</p>",
        "editor": [
            {
                "@id": "https://orcid.org/0000-0001-8135-3489",
                "@type": "Person",
                "affiliation": [
                    {"@type": "Organization", "name": "CERN"},
                    {"@type": "Organization", "name": "TU Wien"},
                ],
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "name": "Nielsen, Lars Holm",
            },
            {
                "@type": "Person",
                "familyName": "Dirk",
                "givenName": "Dirkin",
                "name": "Dirk, Dirkin",
            },
        ],
        "encodingFormat": "application/pdf",
        "funding": [
            {
                "funder": {
                    "@id": "00k4n6c32",
                    "@type": "Organization",
                    "name": "European Commission",
                },
                "name": "Launching of the research program on meaning processing "
                "(111023)",
                "url": {"identifier": "https://sandbox.zenodo.org/", "scheme": "url"},
            }
        ],
        "identifier": "https://doi.org/10.1234/12345-abcde",
        "inLanguage": {"@type": "Language", "alternateName": "dan", "name": "Danish"},
        "keywords": "Abdominal Injuries, custom",
        "license": "https://creativecommons.org/licenses/by/4.0/legalcode",
        "name": "InvenioRDM",
        "publisher": {"@type": "Organization", "name": "InvenioRDM"},
        "size": "9.0 B",
        "temporal": ["1939/1945"],
        "url": "https://127.0.0.1:5000/records/12345-abcde",
        "version": "v1.0",
        # "spatialCoverage": [
        #     {
        #         "geoLocationPoint": {
        #             "pointLatitude": -32.94682,
        #             "pointLongitude": -60.63932,
        #         },
        #         "geoLocationPlace": "test location place",
        #     }
        # ],
        # "funder": [
        #     {
        #         "funderName": "European Commission",
        #         "funderIdentifier": "00k4n6c32",
        #         "funderIdentifierType": "ROR",
        #         "awardTitle": (
        #             "Personalised Treatment For Cystic Fibrosis Patients With "
        #             "Ultra-rare CFTR Mutations (and beyond)"
        #         ),
        #         "awardNumber": "755021",
        #         "awardURI": "https://cordis.europa.eu/project/id/755021",
        #     }
        # ],
    }

    serializer = SchemaorgJSONLDSerializer()
    serialized_record = serializer.dump_obj(full_record_to_dict)

    assert serialized_record["dateModified"]
    assert serialized_record["dateCreated"]

    # Delete to facilitate the comparison with the expected data
    del serialized_record["dateModified"]
    del serialized_record["dateCreated"]

    assert serialized_record == expected_data


def test_schemaorg_serializer_minimal_record(running_app, minimal_record):
    """Test Schemaorg JSON-LD serializer with minimal record."""

    expected_data = {
        "@context": "http://schema.org",
        "@type": "https://schema.org/Photograph",
        "author": [
            {
                "@type": "Person",
                "familyName": "Brown",
                "givenName": "Troy",
            },
            {
                "@type": "Organization",
                "name": "Troy Inc.",
            },
        ],
        "creator": [
            {
                "@type": "Person",
                "familyName": "Brown",
                "givenName": "Troy",
            },
            {
                "@type": "Organization",
                "name": "Troy Inc.",
            },
        ],
        "name": "A Romans story",
        "publisher": {"@type": "Organization", "name": "Acme Inc"},
        "datePublished": "2020-06-01",
    }

    serializer = SchemaorgJSONLDSerializer()
    serialized_record = serializer.dump_obj(minimal_record)

    assert serialized_record == expected_data


def test_schemaorg_serializer_empty_record(running_app, empty_record):
    """Test Schemaorg JSON-LD serializer with minimal record."""

    expected_data = {
        "@context": "http://schema.org",
    }

    serializer = SchemaorgJSONLDSerializer()
    serialized_record = serializer.dump_obj(empty_record)

    assert serialized_record == expected_data
