# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2021 Caltech.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers.schemaorg import (
    SchemaorgJSONLDSerializer,
)


@pytest.fixture(scope="function")
def updated_minimal_record(minimal_record):
    """Update fields (done after record create) for Schemaorg JSON serializer."""
    minimal_record["@context"] = "http://schema.org"
    minimal_record["@type"] = "Photograph"
    minimal_record["@id"] = "https://doi.org/10.5281/inveniordm.5678"

    return minimal_record


@pytest.fixture(scope="function")
def updated_full_record(full_record):
    """Update fields (done after record create) for Schemaorg JSON serializer."""
    full_record["@context"] = "http://schema.org"
    full_record["@type"] = "Photograph"
    full_record["@id"] = "https://doi.org/10.5281/inveniordm.5678"

    return full_record


def test_schemaorg_serializer_full_record(running_app, full_record):
    """Test Schemaorg JSON-LD serializer with full record."""

    expected_data = {
        "@context": "http://schema.org",
        "@id": "https://doi.org/10.1234/inveniordm.1234",
        "@type": "https://schema.org/Photograph",
        "author": [
            {
                "@id": "https://orcid.org/0000-0001-8135-3489",
                "@type": "Person",
                "name": "Nielsen, Lars Holm",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "affiliation": [
                    {
                        "@id": "https://ror.org/01ggx4157",
                        "@type": "Organization",
                        "name": "CERN",
                    },
                    {"@type": "Organization", "name": "free-text"},
                ],
            }
        ],
        "creator": [
            {
                "@id": "https://orcid.org/0000-0001-8135-3489",
                "@type": "Person",
                "name": "Nielsen, Lars Holm",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "affiliation": [
                    {
                        "@id": "https://ror.org/01ggx4157",
                        "@type": "Organization",
                        "name": "CERN",
                    },
                    {"@type": "Organization", "name": "free-text"},
                ],
            }
        ],
        "datePublished": "2018",
        "description": "<h1>A description</h1> <p>with HTML tags</p>",
        "editor": [
            {
                "@id": "https://orcid.org/0000-0001-8135-3489",
                "@type": "Person",
                "name": "Nielsen, Lars Holm",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "affiliation": [
                    {
                        "@id": "https://ror.org/01ggx4157",
                        "@type": "Organization",
                        "name": "CERN",
                    },
                ],
            }
        ],
        "encodingFormat": "application/pdf",
        "funding": [
            {
                "funder": {"@type": "Organization", "@id": "00k4n6c32"},
                "identifier": "00k4n6c32::755021",
            }
        ],
        "identifier": "https://doi.org/10.1234/inveniordm.1234",
        "inLanguage": {"@type": "Language", "alternateName": "dan", "name": "Danish"},
        "keywords": "custom",
        "license": "https://creativecommons.org/licenses/by/4.0/legalcode",
        "name": "InvenioRDM",
        "publisher": {"@type": "Organization", "name": "InvenioRDM"},
        "version": "v1.0",
        "temporal": ["1939/1945"],
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
    serialized_record = serializer.dump_obj(full_record)

    assert serialized_record["dateModified"]

    # Delete to facilitate the comparison with the expected data
    del serialized_record["dateModified"]

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
