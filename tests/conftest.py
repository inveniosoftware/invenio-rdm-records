# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from collections import namedtuple

import pytest
from flask_principal import Identity, Need, UserNeed
from flask_security import login_user
from flask_security.utils import hash_password
from invenio_access.permissions import system_identity
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_app as _create_app
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_rdm_records import config
from invenio_rdm_records.records.api import RDMParent
from invenio_rdm_records.vocabularies import Vocabularies


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
        'RECORDS_PERMISSIONS_RECORD_POLICY',
        'RECORDS_REST_ENDPOINTS',
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    app_config['RECORDS_REFRESOLVER_CLS'] = \
        "invenio_records.resolver.InvenioRefResolver"
    app_config['RECORDS_REFRESOLVER_STORE'] = \
        "invenio_jsonschemas.proxies.current_refresolver_store"

    # Variable not used. We set it to silent warnings
    app_config['JSONSCHEMAS_HOST'] = 'not-used'

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
                "identifier": "10.5281/inveniordm.1234",
                "provider": "datacite",
                "client": "inveniordm"
            },
        },
        "metadata": {
            "resource_type": {"id": "image-photo"},
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
                "lang": {
                    "id": "eng"
                }
            }],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [{
                "id": "A-D000007"
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
            "languages": [{"id": "dan"}, {"id": "eng"}],
            "identifiers": [{
                "identifier": "1924MNRAS..84..308E",
                "scheme": "bibcode"
            }],
            "related_identifiers": [{
                "identifier": "10.1234/foo.bar",
                "scheme": "doi",
                "relation_type": "cites",
                "resource_type": {"id": "dataset"}
            }],
            "sizes": [
                "11 pages"
            ],
            "formats": [
                "application/pdf"
            ],
            "version": "v1.0",
            "rights": [{
                "title": "Creative Commons Attribution 4.0 International",
                "scheme": "spdx",
                "identifier": "cc-by-4.0",
                "link": "https://creativecommons.org/licenses/by/4.0/"
            }],
            "description": "Test",
            "additional_descriptions": [{
                "description": "Bla bla bla",
                "type": "methods",
                "lang": {
                    "id": "eng"
                }
            }],
            "locations": [{
                "geometry": {
                    "type": "Point",
                    "coordinates": [-32.94682, -60.63932]
                },
                "place": "test location place",
                "description": "test location description",
                "identifiers": [
                    {
                        "identifier": "12345abcde",
                        "scheme": "wikidata"
                    }, {
                        "identifier": "12345abcde",
                        "scheme": "geonames"
                    }
                ],
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
                "identifier": "0000 0001 1456 7559",
                "scheme": "isni"
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
            "embargo": {
                "active": True,
                "until": "2131-01-01",
                "reason": "Only for medical doctors."
            }
        },
        "files": {
            "enabled": True,
            "total_size": 1114324524355,
            "count": 1,
            "bucket": "81983514-22e5-473a-b521-24254bd5e049",
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
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "publication_date": "2020-06-01",
            "resource_type": {"id": "image-photo"},
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
def parent(app, db):
    """A parent record."""
    # The parent record is not automatically created when using RDMRecord.
    return RDMParent.create({})


@pytest.fixture()
def users(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(email="info@inveniosoftware.org",
                                      password=hash_password("password"),
                                      active=True)
        user2 = datastore.create_user(email="ser-testalot@inveniosoftware.org",
                                      password=hash_password("beetlesmasher"),
                                      active=True)

    db.session.commit()
    return [user1, user2]


@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)
    return client


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


@pytest.fixture(scope="function")
def identity_simple(users):
    """Simple identity fixture."""
    user = users[0]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method='system_role', value='any_user'))
    i.provides.add(Need(method='system_role', value='authenticated_user'))
    return i


@pytest.fixture(scope='function')
def vocabulary_clear(app):
    """Clears the Vocabulary singleton and pushes an application context.

    NOTE: app fixture pushes an application context
    """
    Vocabularies.clear()


@pytest.fixture(scope="module")
def languages_type(app):
    """Lanuage vocabulary type."""
    return vocabulary_service.create_type(system_identity, "languages", "lng")


@pytest.fixture(scope="module")
def languages_v(app, languages_type):
    """Language vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "eng",
        "title": {
            "en": "English",
            "da": "Engelsk",
        },
        "tags": ["individual", "living"],
        "type": "languages"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "resource_types", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(system_identity, {  # create base resource type
        "id": "image",
        "props": {
            "csl": "figure",
            "datacite_general": "Image",
            "datacite_type": "",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/ImageObject",
            "subtype": "",
            "subtype_name": "",
            "type": "image",
            "type_icon": "chart bar outline",
            "type_name": "Image",
        },
        "title": {
            "en": "Image"
        },
        "type": "resource_types"
    })

    vocab = vocabulary_service.create(system_identity, {
        "id": "image-photo",
        "props": {
            "csl": "graphic",
            "datacite_general": "Image",
            "datacite_type": "Photo",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/Photograph",
            "subtype": "image-photo",
            "subtype_name": "Photo",
            "type": "image",
            "type_icon": "chart bar outline",
            "type_name": "Image",
        },
        "title": {
            "en": "Photo"
        },
        "type": "resource_types"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def subject_type(app):
    """Subject vocabulary type."""
    return vocabulary_service.create_type(system_identity, "subjects", "sub")


@pytest.fixture(scope="module")
def subject_v(app, subject_type):
    """Subject vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "A-D000007",
        "props": {
            "subjectScheme": "MeSH"
        },
        "tags": ["mesh"],
        "title": {
            "en": "Abdominal Injuries"
        },
        "type": "subjects"
    })

    Vocabulary.index.refresh()

    return vocab


RunningApp = namedtuple("RunningApp", [
    "app", "location", "resource_type_v", "subject_v", "languages_v"
])


@pytest.fixture
def running_app(app, location, resource_type_v, subject_v, languages_v):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(app, location, resource_type_v, subject_v, languages_v)
