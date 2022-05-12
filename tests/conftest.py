# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

# Monkey patch Werkzeug 2.1
# Flask-Login uses the safe_str_cmp method which has been removed in Werkzeug
# 2.1. Flask-Login v0.6.0 (yet to be released at the time of writing) fixes the
# issue. Once we depend on Flask-Login v0.6.0 as the minimal version in
# Flask-Security-Invenio/Invenio-Accounts we can remove this patch again.
try:
    # Werkzeug <2.1
    from werkzeug import security
    security.safe_str_cmp
except AttributeError:
    # Werkzeug >=2.1
    import hmac

    from werkzeug import security
    security.safe_str_cmp = hmac.compare_digest

from collections import namedtuple
from copy import deepcopy
from datetime import datetime
from unittest import mock

import arrow
import pytest
from dateutil import tz
from flask import g
from flask_principal import Identity, Need, UserNeed
from flask_security import login_user, logout_user
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles
from invenio_access.permissions import superuser_access, system_identity
from invenio_accounts.models import Role
from invenio_accounts.testutils import login_user_via_session
from invenio_admin.permissions import action_admin_access
from invenio_app.factory import create_app as _create_app
from invenio_cache import current_cache
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_rdm_records import config
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMDraft, RDMParent, RDMRecord
from invenio_rdm_records.services.pids import providers

from .fake_datacite_client import FakeDataCiteClient


#
# User fixture helper - move to pytest-invenio
#
#
# Helper
#
class UserFixture_:
    """A user fixture for easy test user creation."""

    def __init__(self, email=None, password=None, active=True):
        """Constructor."""
        self._email = email
        self._active = active
        self._password = password
        self._identity = None
        self._user = None
        self._client = None

    #
    # Creation
    #
    def create(self, app, db):
        """Create the user."""
        with db.session.begin_nested():
            datastore = app.extensions["security"].datastore
            user = datastore.create_user(
                email=self.email,
                password=hash_password(self.password),
                active=self._active,
            )
        db.session.commit()
        self._user = user
        return self

    #
    # Properties
    #
    @property
    def user(self):
        """Get the user."""
        return self._user

    @property
    def id(self):
        """Get the user id as a string."""
        return str(self._user.id)

    @property
    def email(self):
        """Get the user."""
        return self._email

    @property
    def password(self):
        """Get the user."""
        return self._password

    #
    # App context helpers
    #
    @property
    def identity(self):
        """Create identity for the user."""
        if self._identity is None:
            # Simulate a full login
            assert login_user(self.user)
            self._identity = deepcopy(g.identity)
            # Clean up - we just want the identity object.
            logout_user()
        return self._identity

    @identity.deleter
    def identity(self):
        """Delete the user."""
        self._identity = None

    def app_login(self):
        """Create identity for the user."""
        assert login_user(self.user)

    def app_logout(self):
        """Create identity for the user."""
        assert logout_user()

    @identity.deleter
    def identity(self):
        """Delete the user."""
        self._identity = None

    #
    # Test client helpers
    #
    def login(self, client, logout_first=False):
        """Login the given client."""
        return self._login(client, '/', logout_first)

    def api_login(self, client, logout_first=False):
        """Login the given client."""
        return self._login(client, '/api/', logout_first)

    def logout(self, client):
        """Logout the given client."""
        return self._logout(client, '/')

    def api_logout(self, client):
        """Logout the given client."""
        return self._logout(client, '/api/')

    def _login(self, client, base_path, logout):
        """Login the given client."""
        if logout:
            self._logout(client, base_path)
        res = client.post(
            f'{base_path}login',
            data=dict(email=self.email, password=self.password),
            environ_base={'REMOTE_ADDR': '127.0.0.1'},
            follow_redirects=True,
        )
        assert res.status_code == 200
        return client

    def _logout(self, client, base_path):
        """Logout the client."""
        res = client.get(f'{base_path}logout')
        assert res.status_code < 400
        return client


@pytest.fixture(scope='session')
def UserFixture():
    """Class to create user fixtures from."""
    return UserFixture_


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


def _(x):
    """Identity function for string extraction."""
    return x


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

    # OAI Server
    app_config["OAISERVER_ID_PREFIX"] = 'oai:inveniosoftware.org:recid/'
    app_config["OAISERVER_RECORD_INDEX"] = 'rdmrecords-records'
    app_config['OAISERVER_METADATA_FORMATS'] = {
        'oai_dc': {
            'serializer': 'invenio_rdm_records.oai:dublincore_etree',
            'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
            'namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        },
        'datacite': {
            'serializer': 'invenio_rdm_records.oai:datacite_etree',
            'schema': 'http://schema.datacite.orgmeta/nonexistant/nonexistant.xsd',  # noqa
            'namespace': 'http://datacite.org/schema/nonexistant',
        },
        'oai_datacite': {
            'serializer': 'invenio_rdm_records.oai:oai_datacite_etree',
            'schema': 'http://schema.datacite.org/oai/oai-1.1/oai.xsd',
            'namespace': 'http://schema.datacite.org/oai/oai-1.1/',
        },
    }
    app_config["INDEXER_DEFAULT_INDEX"] = "rdmrecords-records-record-v5.0.0"
    # Variable not used. We set it to silent warnings
    app_config['JSONSCHEMAS_HOST'] = 'not-used'

    # Enable DOI minting...
    app_config['DATACITE_ENABLED'] = True
    app_config['DATACITE_USERNAME'] = 'INVALID'
    app_config['DATACITE_PASSWORD'] = 'INVALID'
    app_config['DATACITE_PREFIX'] = '10.1234'
    app_config['DATACITE_DATACENTER_SYMBOL'] = 'TEST'
    # ...but fake it

    app_config['RDM_PERSISTENT_IDENTIFIER_PROVIDERS'] = [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=FakeDataCiteClient("datacite", config_prefix="DATACITE"),
            label=_("DOI"),
        ),
        # DOI provider for externally managed DOIs
        providers.ExternalPIDProvider(
            "external",
            "doi",
            validators=[
                providers.BlockedPrefixes(config_names=['DATACITE_PREFIX'])
            ],
            label=_("DOI"),
        ),
        # OAI identifier
        providers.OAIPIDProvider("oai", label=_("OAI ID"),),
    ]

    return app_config


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return _create_app


def _es_create_indexes(current_search, current_search_client):
    """Create all registered Elasticsearch indexes."""
    to_create = [
        RDMRecord.index._name,
        RDMDraft.index._name,
        Community.index._name,
    ]
    # list to trigger iter
    list(current_search.create(ignore_existing=True, index_list=to_create))
    current_search_client.indices.refresh()


def _es_delete_indexes(current_search):
    """Delete all registered Elasticsearch indexes."""
    to_delete = [
        RDMRecord.index._name,
        RDMDraft.index._name,
        Community.index._name,
    ]
    list(current_search.delete(index_list=to_delete))


# overwrite pytest_invenio.fixture to only delete record indices
# keeping vocabularies.
@pytest.fixture(scope='function')
def es_clear(es):
    """Clear Elasticsearch indices after test finishes (function scope).

    This fixture rollback any changes performed to the indexes during a test,
    in order to leave Elasticsearch in a clean state for the next test.
    """
    from invenio_search import current_search, current_search_client
    yield es
    _es_delete_indexes(current_search)
    _es_create_indexes(current_search, current_search_client)


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
                "affiliations": [{"id": "cern"}, {"name": "free-text"}]
            }],
            "title": "InvenioRDM",
            "additional_titles": [{
                "title": "a research data management platform",
                "type": {
                    "id": "subtitle"
                },
                "lang": {
                    "id": "eng"
                }
            }],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [
                {"id": "http://id.nlm.nih.gov/mesh/A-D000007"},
                {"subject": "custom"}
            ],
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
                "role": {"id": "other"},
                "affiliations": [{"id": "cern"}]
            }],
            "dates": [{
                "date": "1939/1945",
                "type": {"id": "other"},
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
                "relation_type": {"id": "iscitedby"},
                "resource_type": {"id": "dataset"}
            }],
            "sizes": [
                "11 pages"
            ],
            "formats": [
                "application/pdf"
            ],
            "version": "v1.0",
            "rights": [
                {
                    "title": {
                        "en": "A custom license"
                    },
                    "description": {
                        "en": "A description"
                    },
                    "link": "https://customlicense.org/licenses/by/4.0/"
                 },
                {
                    "id": "cc-by-4.0"
                }
            ],
            "description": "<h1>A description</h1> <p>with HTML tags</p>",
            "additional_descriptions": [{
                "description": "Bla bla bla",
                "type": {"id": "methods"},
                "lang": {
                    "id": "eng"
                }
            }],
            "locations": {
                "features": [{
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
                }]
            },
            "funding": [{
                "funder": {
                    "id": "00k4n6c32",
                },
                "award": {
                    "id": "00k4n6c32::755021"
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
            },
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
def minimal_community():
    """Data for a minimal community."""
    return {
        "slug": "blr",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Biodiversity Literature Repository",
            "type": {"id": "topic"}
        }
    }


@pytest.fixture()
def minimal_community2():
    """Data for a minimal community too."""
    return {
        "slug": "rdm",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Research Data Management",
            "type": {"id": "topic"}
        }
    }


@pytest.fixture()
def minimal_oai_set():
    """Data for a minimal OAI-PMH set."""
    return {
        "name": "name",
        "spec": "spec",
        "search_pattern": "is_published:true",
        "description": None,
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
    login_user(user)
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


@pytest.fixture(scope="module")
def languages_type(app):
    """Lanuage vocabulary type."""
    return vocabulary_service.create_type(system_identity, "languages", "lng")


@pytest.fixture(scope="module")
def languages_v(app, languages_type):
    """Language vocabulary record."""
    vocabulary_service.create(system_identity, {
        "id": "dan",
        "title": {
            "en": "Danish",
            "da": "Dansk",
        },
        "props": {"alpha_2": "da"},
        "tags": ["individual", "living"],
        "type": "languages"
    })

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
        system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(system_identity, {
        "id": "dataset",
        "icon": "table",
        "props": {
            "csl": "dataset",
            "datacite_general": "Dataset",
            "datacite_type": '',
            "openaire_resourceType": '21',
            "openaire_type": "dataset",
            "eurepo": "info:eu-repo/semantics/other",
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

    vocabulary_service.create(system_identity, {  # create base resource type
        "id": "image",
        "props": {
            "csl": "figure",
            "datacite_general": "Image",
            "datacite_type": "",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "eurepo": "info:eu-repo/semantic/other",
            "schema.org": "https://schema.org/ImageObject",
            "subtype": "",
            "type": "image",
        },
        "icon": "chart bar outline",
        "title": {
            "en": "Image"
        },
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes"
    })

    vocab = vocabulary_service.create(system_identity, {
        "id": "image-photo",
        "props": {
            "csl": "graphic",
            "datacite_general": "Image",
            "datacite_type": "Photo",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "eurepo": "info:eu-repo/semantic/other",
            "schema.org": "https://schema.org/Photograph",
            "subtype": "image-photo",
            "type": "image",
        },
        "icon": "chart bar outline",
        "title": {
            "en": "Photo"
        },
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def title_type(app):
    """title vocabulary type."""
    return vocabulary_service.create_type(system_identity,
                                          "titletypes", "ttyp")


@pytest.fixture(scope="module")
def title_type_v(app, title_type):
    """Title Type vocabulary record."""
    vocabulary_service.create(system_identity, {
        "id": "subtitle",
        "props": {
            "datacite": "Subtitle"
        },
        "title": {
            "en": "Subtitle"
        },
        "type": "titletypes"
    })

    vocab = vocabulary_service.create(system_identity, {
        "id": "alternative-title",
        "props": {
            "datacite": "AlternativeTitle"
        },
        "title": {
            "en": "Alternative title"
        },
        "type": "titletypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def description_type(app):
    """title vocabulary type."""
    return vocabulary_service.create_type(system_identity,
                                          "descriptiontypes", "dty")


@pytest.fixture(scope="module")
def description_type_v(app, description_type):
    """Title Type vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "methods",
        "title": {
            "en": "Methods"
        },
        "props": {
            "datacite": "Methods"
        },
        "type": "descriptiontypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def subject_v(app):
    """Subject vocabulary record."""
    subjects_service = current_service_registry.get("subjects")
    vocab = subjects_service.create(system_identity, {
        "id": "http://id.nlm.nih.gov/mesh/A-D000007",
        "scheme": "MeSH",
        "subject": "Abdominal Injuries",
    })

    Subject.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def date_type(app):
    """Date vocabulary type."""
    return vocabulary_service.create_type(system_identity, "datetypes", "dat")


@pytest.fixture(scope="module")
def date_type_v(app, date_type):
    """Subject vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "other",
        "title": {
            "en": "Other"
        },
        "props": {
            "datacite": "Other"
        },
        "type": "datetypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Contributor role vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "contributorsroles", "cor"
    )


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Contributor role vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "other",
        "props": {
            "datacite": "Other"
        },
        "title": {
            "en": "Other"
        },
        "type": "contributorsroles"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def relation_type(app):
    """Relation type vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "relationtypes", "rlt"
    )


@pytest.fixture(scope="module")
def relation_type_v(app, relation_type):
    """Relation type vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "iscitedby",
        "props": {
            "datacite": "IsCitedBy"
        },
        "title": {
            "en": "Is cited by"
        },
        "type": "relationtypes"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def licenses(app):
    """Licenses vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "licenses", "lic"
    )


@pytest.fixture(scope="module")
def licenses_v(app, licenses):
    """Licenses vocabulary record."""
    vocab = vocabulary_service.create(system_identity, {
        "id": "cc-by-4.0",
        "props": {
            "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "scheme": "spdx",
            "osi_approved": ""
        },
        "title": {
            "en": "Creative Commons Attribution 4.0 International"
        },
        "tags": [
            "recommended",
            "all"
        ],
        "description": {
            "en": "The Creative Commons Attribution license allows"
                  " re-distribution and re-use of a licensed work on"
                  " the condition that the creator is appropriately credited."
        },
        "type": "licenses"
    })

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def affiliations_v(app):
    """Affiliation vocabulary record."""
    affiliations_service = (
        current_service_registry.get("affiliations")
    )
    aff = affiliations_service.create(system_identity, {
        "id": "cern",
        "name": "CERN",
        "acronym": "CERN",
        "identifiers": [{
            "scheme": "ror",
            "identifier": "01ggx4157",
        }, {
            "scheme": "isni",
            "identifier": "000000012156142X",
        }]
    })

    Affiliation.index.refresh()

    return aff


@pytest.fixture(scope="module")
def funders_v(app):
    """Funder vocabulary record."""
    funders_service = current_service_registry.get("funders")
    funder = funders_service.create(system_identity, {
        "id": "00k4n6c32",
        "identifiers": [
            {
                "identifier": "000000012156142X",
                "scheme": "isni",
            },
            {
                "identifier": "00k4n6c32",
                "scheme": "ror",
            }
        ],
        "name": "European Commission",
        "title": {
            "en": "European Commission",
            "fr": "Commission européenne",
        },
        "country": "BE"
    })

    Funder.index.refresh()

    return funder


@pytest.fixture(scope="module")
def awards_v(app, funders_v):
    """Funder vocabulary record."""
    awards_service = current_service_registry.get("awards")
    award = awards_service.create(system_identity, {
        "id": "755021",
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url"
            }
        ],
        "number": "755021",
        "title": {
            "en": (
                "Personalised Treatment For Cystic Fibrosis Patients With "
                "Ultra-rare CFTR Mutations (and beyond)"
            ),
        },
        "funder": {
            "id": "00k4n6c32"
        },
        "acronym": "HIT-CF",
    })

    Award.index.refresh()

    return award


@pytest.fixture(scope="function")
def cache():
    """Empty cache."""
    try:
        current_cache.clear()
        yield current_cache
    finally:
        current_cache.clear()


RunningApp = namedtuple("RunningApp", [
    "app",
    "superuser_identity",
    "location",
    "cache",
    "resource_type_v",
    "subject_v",
    "languages_v",
    "affiliations_v",
    "title_type_v",
    "description_type_v",
    "date_type_v",
    "contributors_role_v",
    "relation_type_v",
    "licenses_v",
    "funders_v",
    "awards_v",
])


@pytest.fixture
def running_app(
    app, superuser_identity, location, cache, resource_type_v, subject_v,
    languages_v, affiliations_v, title_type_v, description_type_v,
    date_type_v, contributors_role_v, relation_type_v, licenses_v,
    funders_v, awards_v,
):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(
        app,
        superuser_identity,
        location,
        cache,
        resource_type_v,
        subject_v,
        languages_v,
        affiliations_v,
        title_type_v,
        description_type_v,
        date_type_v,
        contributors_role_v,
        relation_type_v,
        licenses_v,
        funders_v,
        awards_v,
    )


@pytest.fixture(scope="function")
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture(scope="function")
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture(scope="function")
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="admin-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=action_admin_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def embargoed_record(running_app, minimal_record, superuser_identity):
    """Embargoed record."""
    service = current_rdm_records.records_service
    today = arrow.utcnow().date().isoformat()

    # Add embargo to record
    with mock.patch('arrow.utcnow') as mock_arrow:
        minimal_record["access"]["files"] = 'restricted'
        minimal_record["access"]["status"] = 'embargoed'
        minimal_record["access"]["embargo"] = dict(
            active=True, until=today, reason=None
        )

        # We need to set the current date in the past to pass the validations
        mock_arrow.return_value = arrow.get(
            datetime(1954, 9, 29), tz.gettz('UTC')
        )
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(id_=draft.id, identity=superuser_identity)

        RDMRecord.index.refresh()

        # Recover current date
        mock_arrow.return_value = arrow.get(datetime.utcnow())

    return record


@pytest.fixture()
def uploader(UserFixture, app, db):
    """Curator."""
    u = UserFixture(
        email="uploader@inveniosoftware.org",
        password="uploader",
    )
    u.create(app, db)
    return u


@pytest.fixture()
def curator(UserFixture, app, db):
    """Curator."""
    u = UserFixture(
        email="curator@inveniosoftware.org",
        password="curator",
    )
    u.create(app, db)
    return u


@pytest.fixture()
def community_type_type(superuser_identity):
    """Creates and retrieves a language vocabulary type."""
    v = vocabulary_service.create_type(
        superuser_identity, "communitytypes", "comtyp")
    return v


@pytest.fixture()
def community_type_record(superuser_identity, community_type_type):
    """Creates a d retrieves community type records."""
    record = vocabulary_service.create(
        identity=superuser_identity,
        data={
            "id": 'topic',
            "title": {"en": "Topic"},
            'type': 'communitytypes',
        },
    )
    Vocabulary.index.refresh()  # Refresh the index

    return record


@pytest.fixture()
def community(running_app, community_type_record, curator, minimal_community):
    """Get the current RDM records service."""
    c = current_communities.service.create(
        curator.identity,
        minimal_community,
    )
    Community.index.refresh()
    return c


@pytest.fixture(scope="session")
def headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/json',
    }


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "admin-access")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u
