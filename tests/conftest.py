# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, Need, UserNeed
from invenio_app.factory import create_app as _create_app

from invenio_rdm_records import config


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


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
        'PIDSTORE_RECID_FIELD',
        'RECORDS_REST_ENDPOINTS',
        'RECORDS_PERMISSIONS_RECORD_POLICY'
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    return app_config


@pytest.fixture(scope='module')
def create_app():
    """Create app fixture for UI+API app."""
    return _create_app


@pytest.fixture(scope='function')
def full_record(users):
    """Full record data as dict coming from the external world."""
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
                "person_or_org": {
                    "name": "Nielsen, Lars Holm",
                    "type": "personal",
                    "given_name": "Lars Holm",
                    "family_name": "Nielsen",
                    "identifiers": [{
                        "scheme": "orcid",
                        "identifier": "0000-0001-8135-3489"
                    }],
                },
                "affiliations": [{
                    "name": "CERN",
                    "identifiers": [{
                        "scheme": "ror",
                        "identifier": "01ggx4157",
                    }, {
                        "scheme": "isni",
                        "identifier": "000000012156142X",
                    }]
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
                "person_or_org": {
                    "name": "Nielsen, Lars Holm",
                    "type": "personal",
                    "given_name": "Lars Holm",
                    "family_name": "Nielsen",
                    "identifiers": [{
                        "scheme": "orcid",
                        "identifier": "0000-0001-8135-3489"
                    }],
                },
                "role": "other",
                "affiliations": [{
                    "name": "CERN",
                    "identifiers": [{
                        "scheme": "ror",
                        "identifier": "01ggx4157",
                    }, {
                        "scheme": "isni",
                        "identifier": "000000012156142X",
                    }]
                }]
            }],
            "dates": [{
                "date": "1939/1945",
                "type": "other",
                "description": "A date"
            }],
            "languages": [{"id": "da"}, {"id": "en"}],
            "identifiers": [{
                "identifier": "1924MNRAS..84..308E",
                "scheme": "bibcode"
            }],
            "related_identifiers": [{
                "identifier": "10.1234/foo.bar",
                "scheme": "doi",
                "relation_type": "cites",
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
                "user": users[0].id
            },
            "on_behalf_of": {
                "user": users[1].id
            }
        },
        "access": {
            "record": "public",
            "files": "restricted",
            "owned_by": [{
                "user": users[0].id
            }],
            "embargo": {
                "active": True,
                "until": "2131-01-01",
                "reason": "Only for medical doctors."
            }
        },
        "files": {
            "enabled": True,
            "default_preview": "big-dataset.zip",
            "order": ["big-dataset.zip"],
            "entries": {
                "big-dataset.zip": {
                    "checksum": "md5:234245234213421342",
                    "mimetype": "application/zip",
                    "size": 1114324524355,
                    "key": "big-dataset.zip",
                    "file_id": "445aaacd-9de1-41ab-af52-25ab6cb93df7"
                }
            },
            "meta": {
                "big-dataset.zip": {
                    "description": "File containing the data."
                }
            }
        },
        "notes": [
            "Under investigation for copyright infringement."
        ]
    }


@pytest.fixture(scope='function')
def minimal_record(users):
    """Minimal record data as dict coming from the external world."""
    return {
        "access": {
            "record": "public",
            "files": "public",
            "owned_by": [{"user": users[0].id}],
        },
        "metadata": {
            "publication_date": "2020-06-01",
            "resource_type": {
                "type": "image",
                "subtype": "image-photo"
            },
            "creators": [{
                "person_or_org": {
                    "family_name": "Brown",
                    "given_name": "Troy",
                    "type": "personal"
                }
            }, {
                "person_or_org": {
                    "name": "Troy Inc.",
                    "type": "organizational",
                },
            }],
            "title": "A Romans story"
        }
    }


@pytest.fixture()
def users(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(email="info@inveniosoftware.org",
                                      password="password", active=True)
        user2 = datastore.create_user(email="ser-testalot@inveniosoftware.org",
                                      password="beetlesmasher", active=True)

    db.session.commit()
    return [user1, user2]


@pytest.fixture()
def roles(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        role1 = datastore.create_role(name="test",
                                      description="role for testing purposes")
        role2 = datastore.create_role(name="strong",
                                      description="tests are coming")

    db.session.commit()
    return [role1, role2]


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method='system_role', value='any_user'))
    return i
