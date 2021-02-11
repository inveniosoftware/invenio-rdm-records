# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_api

from invenio_rdm_records import config


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='module')
def app_config(app_config):
    """Override pytest-invenio app_config fixture.

    For test purposes we need to enforce the configuration variables set in
    config.py. Because invenio-rdm-records is not a flavour extension, it does
    not enforce them via a config entrypoint or ext.py; only flavour
    extensions are allowed to forcefully set configuration.

    This means there is a clash between configuration set by
    invenio-records-rest and this module for instance. We want this module's
    config.py to apply in tests.
    """
    supported_configurations = [
        'FILES_REST_PERMISSION_FACTORY',
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    # Temporarly force to delete records rest default endpoints until
    # we completely remove the dependency on the module
    app_config["RECORDS_REST_ENDPOINTS"] = {}

    return app_config


@pytest.fixture(scope='function')
def full_record():
    """Full record dereferenced data, as is expeceted by the UI serializer."""
    return {
        "pids": {
            "doi": {
                "identifier": "10.5281/zenodo.1234",
                "provider": "datacite",
                "client": "zenodo"
            },
            "concept-doi": {
                "identifier": "10.5281/zenodo.1234",
                "provider": "datacite",
                "client": "zenodo"
            },
            "handle": {
                "identifier": "9.12314",
                "provider": "cern-handle",
                "client": "zenodo"
            },
            "oai": {
                "identifier": "oai:zenodo.org:12345",
                "provider": "zenodo"
            }
        },
        "metadata": {
            "resource_type": {
                "type": "publication",
                "subtype": "publication-article"
            },
            "creators": [{
                "name": "Nielsen, Lars Holm",
                "type": "personal",
                "given_name": "Lars Holm",
                "family_name": "Nielsen",
                "identifiers": {
                    "orcid": "0000-0001-8135-3489"
                },
                "affiliations": [{
                    "name": "CERN",
                    "identifiers": {
                        "ror": "01ggx4157",
                        "isni": "000000012156142X"
                    }
                }]
            }],
            "title": "InvenioRDM",
            "additional_titles": [{
                "title": "a research data management platform",
                "type": "subtitle",
                "lang": "eng"
            }],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [{
                "subject": "test",
                "identifier": "test",
                "scheme": "dewey"
            }],
            "contributors": [{
                "name": "Nielsen, Lars Holm",
                "type": "personal",
                "role": "other",
                "given_name": "Lars Holm",
                "family_name": "Nielsen",
                "identifiers": {
                    "orcid": "0000-0001-8135-3489"
                },
                "affiliations": [{
                    "name": "CERN",
                    "identifiers": {
                        "ror": "01ggx4157",
                        "isni": "000000012156142X"
                    }
                }]
            }],
            "dates": [{
                "date": "1939/1945",
                "type": "other",
                "description": "A date"
            }],
            "languages": [{
                "id": "da",
                "metadata": {"title": {"en": "Danish"}}
            }, {
                "id": "en",
                "metadata": {"title": {"en": "English"}}
            }],
            "identifiers": [{
                "identifier": "1924MNRAS..84..308E",
                "scheme": "bibcode"
            }],
            "related_identifiers": [{
                "identifier": "10.1234/foo.bar",
                "scheme": "doi",
                "relation": "cites",
                "resource_type": {"type": "dataset"}
            }],
            "sizes": [
                "11 pages"
            ],
            "formats": [
                "application/pdf"
            ],
            "version": "v1.0",
            "rights": [{
                "rights": "Creative Commons Attribution 4.0 International",
                "scheme": "spdx",
                "identifier": "cc-by-4.0",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            }],
            "description": "Test",
            "additional_descriptions": [{
                "description": "Bla bla bla",
                "type": "methods",
                "lang": "eng"
            }],
            "locations": [{
                "point": {
                    "lat": 1,
                    "lon": 2
                },
                "place": "home",
                "description": "test"
            }],
            "funding": [{
                "funder": {
                    "name": "European Commission",
                    "identifier": "1234",
                    "scheme": "ror"
                },
                "award": {
                    "title": "OpenAIRE",
                    "number": "246686",
                    "identifier": ".../246686",
                    "scheme": "openaire"
                }
            }],
            "references": [{
                "reference": "Nielsen et al,..",
                "identifier": "101.234",
                "scheme": "doi"
            }]
        },
        "ext": {
            "dwc": {
                "collectionCode": "abc",
                "collectionCode2": 1.1,
                "collectionCode3": True,
                "test": ["abc", 1, True]
            }
        },
        "provenance": {
            "created_by": {
                "user": 1
            },
            "on_behalf_of": {
                "user": 2
            }
        },
        "access": {
            "record": "public",
            "files": "restricted",
            "owned_by": [{
                "user": 1
            }],
            "embargo": {
                "active": True,
                "until": "2131-01-01",
                "reason": "Only for medical doctors."
            },
            "grants": [
                {"subject": "user", "id": "1", "level": "manage"}
            ]
        },
        "files": {
            "disabled": False,
            "total_size": 1114324524355,
            "count": 1,
            "bucket": "81983514-22e5-473a-b521-24254bd5e049",
            "files": [{
                "checksum": "md5:234245234213421342",
                "size": 1114324524355,
                "key": "big-dataset.zip",
                "ext": "zip",
                "description": "File containing the data.",
                "order": "1",
                "default_preview": True,
                "identifier": "445aaacd-9de1-41ab-af52-25ab6cb93df7"
            }]
        },
        "notes": [
            "Under investigation for copyright infringement."
        ]
    }


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/json',
    }
