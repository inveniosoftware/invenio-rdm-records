# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2025 CERN.
# Copyright (C) 2019-2022 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from invenio_rdm_records.services.permissions import RDMRequestsPermissionPolicy

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
from io import BytesIO
from unittest import mock

import arrow
import pytest
from dateutil import tz
from flask_principal import Identity, Need, RoleNeed, UserNeed
from flask_security import login_user
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles
from invenio_access.permissions import superuser_access, system_identity
from invenio_accounts.models import Role
from invenio_accounts.testutils import login_user_via_session
from invenio_administration.permissions import administration_access_action
from invenio_app.factory import create_app as _create_app
from invenio_cache import current_cache
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_communities.notifications.builders import (
    CommunityInvitationSubmittedNotificationBuilder,
)
from invenio_notifications.backends import EmailNotificationBackend
from invenio_notifications.proxies import current_notifications_manager
from invenio_notifications.services.builders import NotificationBuilder
from invenio_oauth2server.models import Client
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver
from invenio_records_resources.services.custom_fields import TextCF
from invenio_requests.notifications.builders import (
    CommentRequestEventCreateNotificationBuilder,
)
from invenio_users_resources.permissions import user_management_action
from invenio_users_resources.proxies import current_users_service
from invenio_users_resources.records.api import UserAggregate
from invenio_users_resources.services.schemas import (
    NotificationPreferences,
    UserPreferencesSchema,
    UserSchema,
)
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from marshmallow import fields
from werkzeug.local import LocalProxy

from invenio_rdm_records import config
from invenio_rdm_records.notifications.builders import (
    CommunityInclusionAcceptNotificationBuilder,
    CommunityInclusionCancelNotificationBuilder,
    CommunityInclusionDeclineNotificationBuilder,
    CommunityInclusionExpireNotificationBuilder,
    CommunityInclusionSubmittedNotificationBuilder,
    GrantUserAccessNotificationBuilder,
    GuestAccessRequestAcceptNotificationBuilder,
    GuestAccessRequestSubmitNotificationBuilder,
    GuestAccessRequestTokenCreateNotificationBuilder,
    UserAccessRequestAcceptNotificationBuilder,
    UserAccessRequestSubmitNotificationBuilder,
)
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMParent, RDMRecord
from invenio_rdm_records.requests.entity_resolvers import (
    EmailResolver,
    RDMRecordServiceResultResolver,
)
from invenio_rdm_records.resources.serializers import DataCite43JSONSerializer
from invenio_rdm_records.services.communities.components import (
    CommunityServiceComponents,
)
from invenio_rdm_records.services.pids import providers

from .fake_datacite_client import FakeDataCiteClient


class UserPreferencesNotificationsSchema(UserPreferencesSchema):
    """Schema extending preferences with notification preferences for model validation."""

    notifications = fields.Nested(NotificationPreferences)


class NotificationsUserSchema(UserSchema):
    """Schema for dumping a user with preferences including notifications."""

    preferences = fields.Nested(UserPreferencesNotificationsSchema)


class DummyNotificationBuilder(NotificationBuilder):
    """Dummy builder class to do nothing.

    Specific test cases should override their respective builder to test functionality.
    """

    @classmethod
    def build(cls, **kwargs):
        """Build notification based on type and additional context."""
        return {}


@pytest.fixture(scope="module")
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


def _(x):
    """Identity function for string extraction."""
    return x


@pytest.fixture(scope="module")
def mock_datacite_client():
    """Mock DataCite client."""
    return FakeDataCiteClient


@pytest.fixture(scope="module")
def app_config(app_config, mock_datacite_client):
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
        "FILES_REST_PERMISSION_FACTORY",
        "PIDSTORE_RECID_FIELD",
        "RECORDS_PERMISSIONS_RECORD_POLICY",
        "RECORDS_REST_ENDPOINTS",
        "REQUESTS_PERMISSION_POLICY",
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    app_config["THEME_SITENAME"] = "Invenio"

    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )

    # OAI Server
    app_config["OAISERVER_REPOSITORY_NAME"] = "InvenioRDM"
    app_config["OAISERVER_ID_PREFIX"] = "inveniordm"
    app_config["OAISERVER_RECORD_INDEX"] = "rdmrecords-records"
    app_config["OAISERVER_SEARCH_CLS"] = "invenio_rdm_records.oai:OAIRecordSearch"
    app_config["OAISERVER_ID_FETCHER"] = "invenio_rdm_records.oai:oaiid_fetcher"
    app_config["OAISERVER_LAST_UPDATE_KEY"] = "updated"
    app_config["OAISERVER_CREATED_KEY"] = "created"
    app_config["OAISERVER_RECORD_CLS"] = "invenio_rdm_records.records.api:RDMRecord"
    app_config["OAISERVER_RECORD_SETS_FETCHER"] = (
        "invenio_oaiserver.percolator:find_sets_for_record"
    )
    app_config["OAISERVER_GETRECORD_FETCHER"] = (
        "invenio_rdm_records.oai:getrecord_fetcher"
    )
    app_config["OAISERVER_METADATA_FORMATS"] = {
        "marcxml": {
            "serializer": "invenio_rdm_records.oai:marcxml_etree",
            "schema": "https://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd",
            "namespace": "https://www.loc.gov/standards/marcxml/",
        },
        "oai_dc": {
            "serializer": "invenio_rdm_records.oai:dublincore_etree",
            "schema": "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
            "namespace": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        },
        "dcat": {
            "serializer": "invenio_rdm_records.oai:dcat_etree",
            "schema": "http://schema.datacite.org/meta/kernel-4/metadata.xsd",
            "namespace": "https://www.w3.org/ns/dcat",
        },
        "marc21": {
            "serializer": "invenio_rdm_records.oai:marcxml_etree",
            "schema": "https://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd",
            "namespace": "https://www.loc.gov/standards/marcxml/",
        },
        "datacite": {
            "serializer": "invenio_rdm_records.oai:datacite_etree",
            "schema": "http://schema.datacite.org/meta/kernel-4.3/metadata.xsd",
            "namespace": "http://datacite.org/schema/kernel-4",
        },
        "oai_datacite": {
            "serializer": "invenio_rdm_records.oai:oai_datacite_etree",
            "schema": "http://schema.datacite.org/oai/oai-1.1/oai.xsd",
            "namespace": "http://schema.datacite.org/oai/oai-1.1/",
        },
        "datacite4": {
            "serializer": "invenio_rdm_records.oai:datacite_etree",
            "schema": "http://schema.datacite.org/meta/kernel-4.3/metadata.xsd",
            "namespace": "http://datacite.org/schema/kernel-4",
        },
        "oai_datacite4": {
            "serializer": ("invenio_rdm_records.oai:oai_datacite_etree"),
            "schema": "http://schema.datacite.org/oai/oai-1.1/oai.xsd",
            "namespace": "http://schema.datacite.org/oai/oai-1.1/",
        },
    }
    records_index = LocalProxy(
        lambda: current_rdm_records_service.record_cls.index._name
    )
    app_config["OAISERVER_RECORD_INDEX"] = records_index
    app_config["INDEXER_DEFAULT_INDEX"] = records_index

    # Variable not used. We set it to silent warnings
    app_config["JSONSCHEMAS_HOST"] = "not-used"

    # Enable DOI minting...
    app_config["DATACITE_ENABLED"] = True
    app_config["DATACITE_USERNAME"] = "INVALID"
    app_config["DATACITE_PASSWORD"] = "INVALID"
    app_config["DATACITE_PREFIX"] = "10.1234"
    app_config["DATACITE_DATACENTER_SYMBOL"] = "TEST"
    # ...but fake it

    app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=mock_datacite_client("datacite", config_prefix="DATACITE"),
            label=_("DOI"),
        ),
        # DOI provider for externally managed DOIs
        providers.ExternalPIDProvider(
            "external",
            "doi",
            validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
            label=_("DOI"),
        ),
        # OAI identifier
        providers.OAIPIDProvider(
            "oai",
            label=_("OAI ID"),
        ),
    ]
    app_config["RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        # DataCite Concept DOI provider
        providers.DataCitePIDProvider(
            "datacite",
            client=mock_datacite_client("datacite", config_prefix="DATACITE"),
            serializer=DataCite43JSONSerializer(schema_context={"is_parent": True}),
            label=_("Concept DOI"),
        ),
    ]

    # Custom fields
    app_config["RDM_CUSTOM_FIELDS"] = [
        TextCF(name="cern:myfield", use_as_filter=True),
    ]
    app_config["RDM_NAMESPACES"] = {
        "cern": "https://home.cern/",
    }

    # Storage classes
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }

    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"

    app_config["RDM_FILES_DEFAULT_QUOTA_SIZE"] = 10**6
    app_config["RDM_FILES_DEFAULT_MAX_FILE_SIZE"] = 10**6

    # Communities
    app_config["COMMUNITIES_SERVICE_COMPONENTS"] = CommunityServiceComponents

    # TODO: Remove when https://github.com/inveniosoftware/pytest-invenio/pull/95 is
    #       merged and released.
    # Disable rate-limiting
    app_config["RATELIMIT_ENABLED"] = False

    app_config["MAIL_DEFAULT_SENDER"] = "test@invenio-rdm-records.org"

    # Specifying backend for notifications. Only used in specific testcases.
    app_config["NOTIFICATIONS_BACKENDS"] = {
        EmailNotificationBackend.id: EmailNotificationBackend(),
    }

    # Specifying dummy builders to avoid raising errors for most tests. Extend as needed.
    app_config["NOTIFICATIONS_BUILDERS"] = {
        CommentRequestEventCreateNotificationBuilder.type: DummyNotificationBuilder,
        CommunityInclusionAcceptNotificationBuilder.type: DummyNotificationBuilder,
        CommunityInclusionCancelNotificationBuilder.type: DummyNotificationBuilder,
        CommunityInclusionDeclineNotificationBuilder.type: DummyNotificationBuilder,
        CommunityInclusionExpireNotificationBuilder.type: DummyNotificationBuilder,
        CommunityInclusionSubmittedNotificationBuilder.type: DummyNotificationBuilder,
        CommunityInvitationSubmittedNotificationBuilder.type: DummyNotificationBuilder,
        GuestAccessRequestTokenCreateNotificationBuilder.type: GuestAccessRequestTokenCreateNotificationBuilder,
        GuestAccessRequestAcceptNotificationBuilder.type: GuestAccessRequestAcceptNotificationBuilder,
        GuestAccessRequestSubmitNotificationBuilder.type: GuestAccessRequestSubmitNotificationBuilder,
        UserAccessRequestAcceptNotificationBuilder.type: UserAccessRequestAcceptNotificationBuilder,
        UserAccessRequestSubmitNotificationBuilder.type: UserAccessRequestSubmitNotificationBuilder,
        GrantUserAccessNotificationBuilder.type: GrantUserAccessNotificationBuilder,
    }

    # Specifying default resolvers. Will only be used in specific test cases.
    app_config["NOTIFICATIONS_ENTITY_RESOLVERS"] = [
        EmailResolver(),
        RDMRecordServiceResultResolver(),
        ServiceResultResolver(service_id="users", type_key="user"),
        ServiceResultResolver(service_id="communities", type_key="community"),
        ServiceResultResolver(service_id="requests", type_key="request"),
        ServiceResultResolver(service_id="request_events", type_key="request_event"),
    ]

    # Specifying a notifications settings view function to trigger registration of route
    # needed for invenio_url_for
    app_config["NOTIFICATIONS_SETTINGS_VIEW_FUNCTION"] = lambda: "<index>"

    # Extending preferences schemas, to include notification preferences. Should not matter for most test cases
    app_config["ACCOUNTS_USER_PREFERENCES_SCHEMA"] = (
        UserPreferencesNotificationsSchema()
    )
    app_config["USERS_RESOURCES_SERVICE_SCHEMA"] = NotificationsUserSchema

    app_config["RDM_RESOURCE_ACCESS_TOKENS_ENABLED"] = True

    # Disable the automatic creation of moderation requests after publishing a record.
    # When testing unverified users, there is a "unverified_user" fixture for that purpose.
    app_config["ACCOUNTS_DEFAULT_USERS_VERIFIED"] = True
    app_config["RDM_USER_MODERATION_ENABLED"] = False
    app_config["REQUESTS_PERMISSION_POLICY"] = RDMRequestsPermissionPolicy

    app_config["COMMUNITIES_OAI_SETS_PREFIX"] = "community-"

    app_config["APP_RDM_ROUTES"] = {
        "record_detail": "/records/<pid_value>",
        "record_file_download": "/records/<pid_value>/files/<path:filename>",
    }

    app_config["USERS_RESOURCES_GROUPS_ENABLED"] = True
    app_config["THEME_FRONTPAGE"] = False

    return app_config


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entrypoints."""
    return {
        "invenio_base.blueprints": [
            "invenio_app_rdm_records = tests.mock_module:create_invenio_app_rdm_records_blueprint",  # noqa
            "invenio_app_rdm_requests = tests.mock_module:create_invenio_app_rdm_requests_blueprint",  # noqa
            "invenio_app_rdm_communities = tests.mock_module:create_invenio_app_rdm_communities_blueprint",  # noqa
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


def _search_create_indexes(current_search, current_search_client):
    """Create all registered search indexes."""
    to_create = [
        RDMRecord.index._name,
        RDMDraft.index._name,
        Community.index._name,
    ]
    # list to trigger iter
    list(current_search.create(ignore_existing=True, index_list=to_create))
    current_search_client.indices.refresh()


def _search_delete_indexes(current_search):
    """Delete all registered search indexes."""
    to_delete = [
        RDMRecord.index._name,
        RDMDraft.index._name,
        Community.index._name,
    ]
    list(current_search.delete(index_list=to_delete))


# overwrite pytest_invenio.fixture to only delete record indices
# keeping vocabularies.
@pytest.fixture()
def search_clear(search):
    """Clear search indices after test finishes (function scope).

    This fixture rollback any changes performed to the indexes during a test,
    in order to leave search in a clean state for the next test.
    """
    from invenio_search import current_search, current_search_client

    yield search
    _search_delete_indexes(current_search)
    _search_create_indexes(current_search, current_search_client)


@pytest.fixture()
def full_record(users):
    """Full record data as dict coming from the external world."""
    return {
        "pids": {
            "doi": {
                "identifier": "10.1234/inveniordm.1234",
                "provider": "datacite",
                "client": "inveniordm",
            },
            "oai": {
                "identifier": "oai:vvv.com:abcde-fghij",
                "provider": "oai",
            },
        },
        "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
        "version_id": "1",
        "created": "2023-01-01",
        "updated": "2023-01-02",
        "metadata": {
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
                        ],
                    },
                    "affiliations": [{"id": "cern"}, {"name": "free-text"}],
                }
            ],
            "title": "InvenioRDM",
            "additional_titles": [
                {
                    "title": "a research data management platform",
                    "type": {"id": "subtitle"},
                    "lang": {"id": "eng"},
                }
            ],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [
                {"id": "http://id.nlm.nih.gov/mesh/A-D000007"},
                {"subject": "custom"},
            ],
            "contributors": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
                        ],
                    },
                    "role": {"id": "other"},
                    "affiliations": [{"id": "cern"}],
                }
            ],
            "dates": [
                {
                    "date": "1939/1945",
                    "type": {"id": "other"},
                    "description": "A date",
                }
            ],
            "languages": [{"id": "dan"}, {"id": "eng"}],
            "identifiers": [{"identifier": "1924MNRAS..84..308E", "scheme": "ads"}],
            "related_identifiers": [
                {
                    "identifier": "10.1234/foo.bar",
                    "scheme": "doi",
                    "relation_type": {"id": "iscitedby"},
                    "resource_type": {"id": "dataset"},
                }
            ],
            "sizes": ["11 pages"],
            "formats": ["application/pdf"],
            "version": "v1.0",
            "rights": [
                {
                    "title": {"en": "A custom license"},
                    "description": {"en": "A description"},
                    "link": "https://customlicense.org/licenses/by/4.0/",
                },
                {"id": "cc-by-4.0"},
            ],
            "description": "<h1>A description</h1> <p>with HTML tags</p>",
            "additional_descriptions": [
                {
                    "description": "Bla bla bla",
                    "type": {"id": "methods"},
                    "lang": {"id": "eng"},
                }
            ],
            "locations": {
                "features": [
                    {
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-32.94682, -60.63932],
                        },
                        "place": "test location place",
                        "description": "test location description",
                        "identifiers": [
                            {"identifier": "12345abcde", "scheme": "wikidata"},
                            {"identifier": "12345abcde", "scheme": "geonames"},
                        ],
                    }
                ]
            },
            "funding": [
                {
                    "funder": {
                        "id": "00k4n6c32",
                    },
                    "award": {"id": "00k4n6c32::755021"},
                }
            ],
            "references": [
                {
                    "reference": "Nielsen et al,..",
                    "identifier": "0000 0001 1456 7559",
                    "scheme": "isni",
                }
            ],
        },
        "provenance": {
            "created_by": {"user": users[0].id},
            "on_behalf_of": {"user": users[1].id},
        },
        "access": {
            "record": "public",
            "files": "restricted",
            "embargo": {
                "active": True,
                "until": "2131-01-01",
                "reason": "Only for medical doctors.",
            },
        },
        "files": {
            "enabled": True,
            "total_size": 1114324524355,
            "count": 1,
            "bucket": "81983514-22e5-473a-b521-24254bd5e049",
            "default_preview": "big-dataset.zip",
            "order": ["big-dataset.zip"],
            "entries": [
                {
                    "checksum": "md5:234245234213421342",
                    "mimetype": "application/zip",
                    "size": 1114324524355,
                    "key": "big-dataset.zip",
                    "file_id": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                    "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                    "version_id": "1",
                    "created": "2023-01-01",
                    "updated": "2023-01-02",
                    "object_version_id": "1",
                    "metadata": {},
                    "id": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                }
            ],
            "meta": {"big-dataset.zip": {"description": "File containing the data."}},
        },
        "notes": ["Under investigation for copyright infringement."],
    }


# TODO: use `enhanced_full_record` instead of `full_record` in tests
@pytest.fixture()
def enhanced_full_record(users):
    """Full record data as dict coming from the external world."""
    return {
        "id": "w502q-xzh22",
        "pids": {
            "doi": {
                "identifier": "10.1234/inveniordm.1234",
                "provider": "datacite",
                "client": "inveniordm",
            },
            "oai": {
                "identifier": "oai:invenio-rdm.com:vs40t-1br10",
                "provider": "oai",
            },
        },
        "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
        "version_id": "1",
        "created": "2023-01-01",
        "updated": "2023-01-02",
        "metadata": {
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
                        ],
                    },
                    "affiliations": [{"id": "cern"}, {"name": "free-text"}],
                },
                {
                    "person_or_org": {
                        "family_name": "Tom",
                        "given_name": "Blabin",
                        "name": "Tom, Blabin",
                        "type": "personal",
                    }
                },
            ],
            "title": "InvenioRDM",
            "additional_titles": [
                {
                    "title": "a research data management platform",
                    "type": {
                        "id": "subtitle",
                        "title": {
                            "de": "Alternativer Titel",
                            "en": "Alternative title",
                        },
                    },
                    "lang": {
                        "id": "eng",
                        "title": {
                            "en": "English",
                        },
                    },
                }
            ],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [
                {
                    "id": "http://www.oecd.org/science/inno/38235147.pdf?1.6",
                    "scheme": "FOS",
                    "subject": "Biological sciences",
                },
                {"subject": "custom"},
            ],
            "contributors": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
                        ],
                    },
                    "role": {
                        "id": "datamanager",
                        "title": {
                            "de": "DatenmanagerIn",
                            "en": "Data manager",
                        },
                    },
                    "affiliations": [{"id": "cern"}, {"name": "TU Wien"}],
                },
                {
                    "person_or_org": {
                        "family_name": "Dirk",
                        "given_name": "Dirkin",
                        "name": "Dirk, Dirkin",
                        "type": "personal",
                    },
                    "role": {
                        "id": "projectmanager",
                        "title": {
                            "de": "ProjektmanagerIn",
                            "en": "Project manager",
                        },
                    },
                },
            ],
            "dates": [
                {
                    "date": "1939/1945",
                    "type": {
                        "id": "other",
                        "title": {
                            "de": "Verfgbar",
                            "en": "Available",
                        },
                    },
                    "description": "A date",
                }
            ],
            "languages": [
                {
                    "id": "dan",
                    "title": {
                        "en": "Danish",
                    },
                },
                {
                    "id": "eng",
                    "title": {
                        "en": "English",
                    },
                },
            ],
            "identifiers": [{"identifier": "1924MNRAS..84..308E", "scheme": "ads"}],
            "related_identifiers": [
                {
                    "identifier": "10.1234/foo.bar",
                    "scheme": "doi",
                    "relation_type": {
                        "id": "iscitedby",
                        "title": {
                            "de": "Setzt fort",
                            "en": "Continues",
                        },
                    },
                    "resource_type": {
                        "id": "dataset",
                        "title": {
                            "de": "Unterrichtseinheit",
                            "en": "Lesson",
                        },
                    },
                }
            ],
            "sizes": ["11 pages"],
            "formats": ["application/pdf"],
            "version": "v1.0",
            "rights": [
                {
                    "title": {"en": "A custom license"},
                    "description": {"en": "A description"},
                    "link": "https://customlicense.org/licenses/by/4.0/",
                },
                {
                    "id": "cc-by-4.0",
                    "icon": "cc-by-icon",
                    "props": {
                        "scheme": "spdx",
                        "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                    },
                },
            ],
            "description": "<h1>A description</h1> <p>with HTML tags</p>",
            "additional_descriptions": [
                {
                    "description": "Bla bla bla",
                    "type": {
                        "id": "methods",
                        "title": {
                            "de": "Technische Informationen",
                            "en": "Technical info",
                        },
                    },
                    "lang": {"id": "eng", "title": {"en": "English"}},
                }
            ],
            "locations": {
                "features": [
                    {
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-32.94682, -60.63932],
                        },
                        "place": "test location place",
                        "description": "test location description",
                        "identifiers": [
                            {"identifier": "12345abcde", "scheme": "wikidata"},
                            {"identifier": "12345abcde", "scheme": "geonames"},
                        ],
                    }
                ]
            },
            "funding": [
                {
                    "funder": {
                        "id": "00k4n6c32",
                        "name": "Academy of Finland",
                    },
                    "award": {
                        "identifiers": [
                            {
                                "identifier": "https://sandbox.zenodo.org/",
                                "scheme": "url",
                            }
                        ],
                        "number": "111023",
                        "title": {
                            "en": "Launching of the research program on meaning processing",
                        },
                    },
                }
            ],
            "references": [
                {
                    "reference": "Nielsen et al,..",
                    "identifier": "0000 0001 1456 7559",
                    "scheme": "isni",
                }
            ],
        },
        "provenance": {
            "created_by": {"user": users[0].id},
            "on_behalf_of": {"user": users[1].id},
        },
        "access": {
            "record": "public",
            "files": "restricted",
            "embargo": {
                "active": True,
                "until": "2131-01-01",
                "reason": "Only for medical doctors.",
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
                    "file_id": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                    "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                    "version_id": "1",
                    "created": "2023-01-01",
                    "updated": "2023-01-02",
                    "object_version_id": "1",
                    "metadata": {},
                    "id": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                }
            },
            "meta": {"big-dataset.zip": {"description": "File containing the data."}},
        },
        "notes": ["Under investigation for copyright infringement."],
    }


@pytest.fixture()
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
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            # because DATACITE_ENABLED is True, this field is required
            "publisher": "Acme Inc",
            "resource_type": {"id": "image-photo"},
            "title": "A Romans story",
        },
    }


@pytest.fixture()
def empty_record():
    """Almost empty record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {},
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {},
    }


@pytest.fixture()
def minimal_restricted_record(minimal_record):
    """Data for restricted record."""
    record = deepcopy(minimal_record)
    record["access"]["record"] = "restricted"
    record["access"]["files"] = "restricted"
    return record


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
            "type": {"id": "topic"},
        },
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
            "type": {"id": "topic"},
        },
    }


@pytest.fixture()
def restricted_minimal_community():
    """Data for a minimal community."""
    return {
        "slug": "restricted-blr",
        "access": {
            "visibility": "restricted",
        },
        "metadata": {
            "title": "Biodiversity Literature Repository",
            "type": {"id": "topic"},
        },
    }


@pytest.fixture()
def open_review_minimal_community(minimal_community):
    """Data for a minimal community that allows direct publish."""
    community = deepcopy(minimal_community)
    community["slug"] = "open-review-community"
    community["access"]["review_policy"] = "open"
    return community


@pytest.fixture()
def closed_review_minimal_community(minimal_community):
    """Data for a minimal community that allows direct publish."""
    community = deepcopy(minimal_community)
    community["slug"] = "closed-review-community"
    community["access"]["review_policy"] = "closed"
    return community


@pytest.fixture()
def closed_submission_minimal_community(minimal_community):
    """Data for a minimal community that restricts record submission."""
    community = deepcopy(minimal_community)
    community["slug"] = "closed-submission-community"
    community["access"]["record_submission_policy"] = "closed"
    return community


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


@pytest.fixture(scope="module")
def moderator_role(app, database):
    """Moderator role."""
    REQUESTS_MODERATION_ROLE = app.config["REQUESTS_MODERATION_ROLE"]
    mod_role = Role(name=REQUESTS_MODERATION_ROLE)
    database.session.add(mod_role)

    action_role = ActionRoles.create(action=user_management_action, role=mod_role)
    database.session.add(action_role)
    database.session.commit()
    return mod_role


@pytest.fixture(scope="module")
def moderator_user(UserFixture, app, database, moderator_role):
    """Admin user for requests."""
    u = UserFixture(
        email="mod@example.org",
        password=hash_password("password"),
        active=True,
    )
    u.create(app, database)
    u.user.roles.append(moderator_role)

    database.session.commit()
    UserAggregate.index.refresh()
    return u


@pytest.fixture(scope="module")
def mod_identity(app, moderator_user):
    """Admin user for requests."""
    idt = Identity(moderator_user.id)
    REQUESTS_MODERATION_ROLE = app.config["REQUESTS_MODERATION_ROLE"]

    # Add Role user_moderator
    idt.provides.add(RoleNeed(REQUESTS_MODERATION_ROLE))
    # Search requires user to be authenticated
    idt.provides.add(Need(method="system_role", value="authenticated_user"))
    return idt


@pytest.fixture()
def users(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
        user2 = datastore.create_user(
            email="ser-testalot@inveniosoftware.org",
            password=hash_password("beetlesmasher"),
            active=True,
        )

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
        role1 = datastore.create_role(
            name="test", description="role for testing purposes"
        )
        role2 = datastore.create_role(name="strong", description="tests are coming")

    db.session.commit()
    return [role1, role2]


@pytest.fixture()
def identity_simple(users):
    """Simple identity fixture."""
    user = users[0]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture()
def anonymous_identity(users):
    """Simple identity fixture."""
    user = users[1]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method="system_role", value="any_user"))
    return i


@pytest.fixture(scope="module")
def languages_type(app):
    """Lanuage vocabulary type."""
    return vocabulary_service.create_type(system_identity, "languages", "lng")


@pytest.fixture(scope="module")
def languages_v(app, languages_type):
    """Language vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dan",
            "title": {
                "en": "Danish",
                "da": "Dansk",
            },
            "props": {"alpha_2": "da"},
            "tags": ["individual", "living"],
            "type": "languages",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {
                "en": "English",
                "da": "Engelsk",
            },
            "tags": ["individual", "living"],
            "type": "languages",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
                "marc21_type": "dataset",
                "marc21_subtype": "",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "image",
            "props": {
                "csl": "figure",
                "datacite_general": "Image",
                "datacite_type": "",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/ImageObject",
                "subtype": "",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "",
            },
            "icon": "chart bar outline",
            "title": {"en": "Image"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "software",
            "props": {
                "csl": "figure",
                "datacite_general": "Software",
                "datacite_type": "",
                "openaire_resourceType": "0029",
                "openaire_type": "software",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/SoftwareSourceCode",
                "subtype": "",
                "type": "image",
                "marc21_type": "software",
                "marc21_subtype": "",
            },
            "icon": "code",
            "title": {"en": "Software"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "photo",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def title_type(app):
    """title vocabulary type."""
    return vocabulary_service.create_type(system_identity, "titletypes", "ttyp")


@pytest.fixture(scope="module")
def title_type_v(app, title_type):
    """Title Type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "subtitle",
            "props": {"datacite": "Subtitle"},
            "title": {"en": "Subtitle"},
            "type": "titletypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "alternative-title",
            "props": {"datacite": "AlternativeTitle"},
            "title": {"en": "Alternative title"},
            "type": "titletypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def description_type(app):
    """title vocabulary type."""
    return vocabulary_service.create_type(system_identity, "descriptiontypes", "dty")


@pytest.fixture(scope="module")
def description_type_v(app, description_type):
    """Title Type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "methods",
            "title": {"en": "Methods"},
            "props": {"datacite": "Methods"},
            "type": "descriptiontypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def subject_v(app):
    """Subject vocabulary record."""
    subjects_service = current_service_registry.get("subjects")
    vocab = subjects_service.create(
        system_identity,
        {
            "id": "http://id.nlm.nih.gov/mesh/A-D000007",
            "scheme": "MeSH",
            "subject": "Abdominal Injuries",
        },
    )

    Subject.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def date_type(app):
    """Date vocabulary type."""
    return vocabulary_service.create_type(system_identity, "datetypes", "dat")


@pytest.fixture(scope="module")
def date_type_v(app, date_type):
    """Subject vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "title": {"en": "Other"},
            "props": {"datacite": "Other", "marc": "oth"},
            "type": "datetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Contributor role vocabulary type."""
    return vocabulary_service.create_type(system_identity, "contributorsroles", "cor")


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Contributor role vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "datamanager",
            "props": {"datacite": "DataManager"},
            "title": {"en": "Data manager"},
            "type": "contributorsroles",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "projectmanager",
            "props": {"datacite": "ProjectManager"},
            "title": {"en": "Project manager"},
            "type": "contributorsroles",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "props": {"datacite": "Other", "marc": "oth"},
            "title": {"en": "Other"},
            "type": "contributorsroles",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def relation_type(app):
    """Relation type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "relationtypes", "rlt")


@pytest.fixture(scope="module")
def relation_types_v(app, relation_type):
    """Relation type vocabulary record."""
    vocab1 = vocabulary_service.create(
        system_identity,
        {
            "id": "iscitedby",
            "props": {"datacite": "IsCitedBy"},
            "title": {"en": "Is cited by"},
            "type": "relationtypes",
        },
    )

    vocab2 = vocabulary_service.create(
        system_identity,
        {
            "id": "hasmetadata",
            "props": {"datacite": "HasMetadata"},
            "title": {"en": "Has metadata"},
            "type": "relationtypes",
        },
    )

    Vocabulary.index.refresh()

    return [vocab1, vocab2]


@pytest.fixture(scope="module")
def licenses(app):
    """Licenses vocabulary type."""
    return vocabulary_service.create_type(system_identity, "licenses", "lic")


@pytest.fixture(scope="module")
def licenses_v(app, licenses):
    """Licenses vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "cc-by-4.0",
            "props": {
                "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                "scheme": "spdx",
                "osi_approved": "",
            },
            "title": {"en": "Creative Commons Attribution 4.0 International"},
            "tags": ["recommended", "all"],
            "description": {
                "en": "The Creative Commons Attribution license allows"
                " re-distribution and re-use of a licensed work on"
                " the condition that the creator is appropriately credited."
            },
            "type": "licenses",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def affiliations_v(app):
    """Affiliation vocabulary record."""
    affiliations_service = current_service_registry.get("affiliations")
    aff = affiliations_service.create(
        system_identity,
        {
            "id": "cern",
            "name": "CERN",
            "acronym": "CERN",
            "identifiers": [
                {
                    "scheme": "ror",
                    "identifier": "01ggx4157",
                },
                {
                    "scheme": "isni",
                    "identifier": "000000012156142X",
                },
            ],
        },
    )

    Affiliation.index.refresh()

    return aff


@pytest.fixture(scope="module")
def funders_v(app):
    """Funder vocabulary record."""
    funders_service = current_service_registry.get("funders")
    funder = funders_service.create(
        system_identity,
        {
            "id": "00k4n6c32",
            "identifiers": [
                {
                    "identifier": "000000012156142X",
                    "scheme": "isni",
                },
                {
                    "identifier": "00k4n6c32",
                    "scheme": "ror",
                },
            ],
            "name": "European Commission",
            "title": {
                "en": "European Commission",
                "fr": "Commission européenne",
            },
            "country": "BE",
        },
    )

    Funder.index.refresh()

    return funder


@pytest.fixture(scope="module")
def awards_v(app, funders_v):
    """Funder vocabulary record."""
    awards_service = current_service_registry.get("awards")
    award = awards_service.create(
        system_identity,
        {
            "id": "00k4n6c32::755021",
            "identifiers": [
                {
                    "identifier": "https://cordis.europa.eu/project/id/755021",
                    "scheme": "url",
                }
            ],
            "number": "755021",
            "title": {
                "en": (
                    "Personalised Treatment For Cystic Fibrosis Patients With "
                    "Ultra-rare CFTR Mutations (and beyond)"
                ),
            },
            "funder": {"id": "00k4n6c32"},
            "acronym": "HIT-CF",
            "program": "H2020",
        },
    )

    Award.index.refresh()

    return award


@pytest.fixture()
def cache():
    """Empty cache."""
    try:
        current_cache.clear()
        yield current_cache
    finally:
        current_cache.clear()


RunningApp = namedtuple(
    "RunningApp",
    [
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
        "relation_types_v",
        "licenses_v",
        "funders_v",
        "awards_v",
        "moderator_role",  # Add moderator role by default to the app
    ],
)


@pytest.fixture
def running_app(
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
    relation_types_v,
    licenses_v,
    funders_v,
    awards_v,
    moderator_role,
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
        relation_types_v,
        licenses_v,
        funders_v,
        awards_v,
        moderator_role,
    )


@pytest.fixture()
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


@pytest.fixture()
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture()
def superuser(UserFixture, app, db, superuser_role_need):
    """Superuser."""
    u = UserFixture(
        email="superuser@inveniosoftware.org",
        password="superuser",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "superuser-access")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u


@pytest.fixture()
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="administration-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=administration_access_action, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def embargoed_files_record(running_app, minimal_record, superuser_identity):
    """Embargoed files record."""
    service = current_rdm_records_service
    today = arrow.utcnow().date().isoformat()

    # Add embargo to record
    with mock.patch("arrow.utcnow") as mock_arrow:
        minimal_record["access"]["files"] = "restricted"
        minimal_record["access"]["status"] = "embargoed"
        minimal_record["access"]["embargo"] = dict(
            active=True, until=today, reason=None
        )

        # We need to set the current date in the past to pass the validations
        mock_arrow.return_value = arrow.get(datetime(1954, 9, 29), tz.gettz("UTC"))
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(id_=draft.id, identity=superuser_identity)

        RDMRecord.index.refresh()

        # Recover current date
        mock_arrow.return_value = arrow.get(datetime.utcnow())

    return record


@pytest.fixture()
def embargoed_record(running_app, minimal_record, superuser_identity):
    """Embargoed record."""
    service = current_rdm_records_service
    today = arrow.utcnow().date().isoformat()

    # Add embargo to record
    with mock.patch("arrow.utcnow") as mock_arrow:
        minimal_record["access"]["record"] = "restricted"
        minimal_record["access"]["status"] = "embargoed"
        minimal_record["access"]["embargo"] = dict(
            active=True, until=today, reason=None
        )

        # We need to set the current date in the past to pass the validations
        mock_arrow.return_value = arrow.get(datetime(1954, 9, 29), tz.gettz("UTC"))
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(id_=draft.id, identity=superuser_identity)

        RDMRecord.index.refresh()

        # Recover current date
        mock_arrow.return_value = arrow.get(datetime.utcnow())

    return record


@pytest.fixture()
def test_user(UserFixture, app, db, index_users):
    """User meant to test permissions."""
    u = UserFixture(
        email="testuser@inveniosoftware.org",
        password="testuser",
    )
    u.create(app, db)
    index_users()
    return u


@pytest.fixture()
def verified_user(UserFixture, app, db):
    """User meant to test 'verified' property of records."""
    u = UserFixture(
        email="verified@inveniosoftware.org",
        password="testuser",
    )
    u.create(app, db)
    u.user.verified_at = datetime.utcnow()
    # Dumping `is_verified` requires authenticated user in tests
    u.identity.provides.add(Need(method="system_role", value="authenticated_user"))
    return u


@pytest.fixture()
def unverified_user(UserFixture, app, db):
    """User meant to test 'verified' property of records."""
    u = UserFixture(
        email="unverified@inveniosoftware.org",
        password="testuser",
    )
    u.create(app, db)
    u.user.verified_at = None
    # Dumping `is_verified` requires authenticated user in tests
    u.identity.provides.add(Need(method="system_role", value="authenticated_user"))
    return u


@pytest.fixture()
def uploader(UserFixture, app, db, index_users):
    """Uploader."""
    u = UserFixture(
        email="uploader@inveniosoftware.org",
        password="uploader",
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
            "notifications": {
                "enabled": True,
            },
        },
        active=True,
        confirmed=True,
    )
    u.create(app, db)
    index_users()

    return u


@pytest.fixture()
def community_owner(UserFixture, app, db, index_users):
    """Community owner."""
    u = UserFixture(
        email="community_owner@inveniosoftware.org",
        password="community_owner",
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
            "notifications": {
                "enabled": True,
            },
        },
        active=True,
        confirmed=True,
    )
    u.create(app, db)
    index_users()
    return u


@pytest.fixture()
def inviter(index_users):
    """Add/invite a user to a community with a specific role."""

    def invite(user_id, community_id, role):
        """Add/invite a user to a community with a specific role."""
        assert role in ["curator", "owner"]
        invitation_data = {
            "members": [
                {
                    "type": "user",
                    "id": user_id,
                }
            ],
            "role": role,
            "visible": True,
        }
        current_communities.service.members.add(
            system_identity, community_id, invitation_data
        )
        index_users()

    return invite


@pytest.fixture()
def curator(UserFixture, community, inviter, app, db):
    """Creates a curator of the community fixture."""
    curator = UserFixture(
        email="curatoruser@inveniosoftware.org",
        password="curatoruser",
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
            "notifications": {
                "enabled": True,
            },
        },
        active=True,
        confirmed=True,
    )
    curator.create(app, db)
    inviter(curator.id, community.id, "curator")
    return curator


@pytest.fixture()
def community_type_type(superuser_identity):
    """Creates and retrieves a language vocabulary type."""
    v = vocabulary_service.create_type(superuser_identity, "communitytypes", "comtyp")
    return v


@pytest.fixture()
def community_type_record(superuser_identity, community_type_type):
    """Creates and retrieves community type records."""
    record = vocabulary_service.create(
        identity=superuser_identity,
        data={
            "id": "topic",
            "title": {"en": "Topic"},
            "type": "communitytypes",
        },
    )
    Vocabulary.index.refresh()  # Refresh the index

    return record


def _community_get_or_create(community_dict, identity):
    """Util to get or create community, to avoid duplicate error."""
    slug = community_dict["slug"]
    try:
        c = current_communities.service.record_cls.pid.resolve(slug)
    except PIDDoesNotExistError:
        c = current_communities.service.create(
            identity,
            community_dict,
        )
        Community.index.refresh()
    return c


@pytest.fixture()
def community(running_app, community_type_record, community_owner, minimal_community):
    """Get the current RDM records service."""
    return _community_get_or_create(minimal_community, community_owner.identity)


@pytest.fixture()
def community2(running_app, community_type_record, community_owner, minimal_community2):
    """Get the current RDM records service."""
    return _community_get_or_create(minimal_community2, community_owner.identity)


@pytest.fixture()
def restricted_community(
    running_app,
    community_type_record,
    community_owner,
    restricted_minimal_community,
):
    """Get the current RDM records service."""
    return _community_get_or_create(
        restricted_minimal_community, community_owner.identity
    )


@pytest.fixture()
def open_review_community(
    running_app,
    community_type_record,
    community_owner,
    open_review_minimal_community,
):
    """Create community with open review policy i.e allow direct publishes."""
    return _community_get_or_create(
        open_review_minimal_community, community_owner.identity
    )


@pytest.fixture()
def closed_review_community(
    running_app,
    community_type_record,
    community_owner,
    closed_review_minimal_community,
):
    """Create community with close review policy i.e allow direct publishes."""
    return _community_get_or_create(
        closed_review_minimal_community, community_owner.identity
    )


@pytest.fixture()
def closed_submission_community(
    running_app,
    community_type_record,
    community_owner,
    closed_submission_minimal_community,
):
    """Create community with close submission policy."""
    return _community_get_or_create(
        closed_submission_minimal_community, community_owner.identity
    )


@pytest.fixture()
def record_community(db, uploader, minimal_record, community):
    """Creates a record that belongs to a community."""

    class Record:
        """Test record class."""

        def create_record(
            self,
            record_dict=minimal_record,
            uploader=uploader,
            community=community,
        ):
            """Creates new record that belongs to the same community."""
            # create draft
            draft = current_rdm_records_service.create(uploader.identity, record_dict)
            record = draft._record
            if community:
                # add the record to the community
                community_record = community._record
                record.parent.communities.add(community_record, default=False)
                record.parent.commit()
                db.session.commit()

            # publish and get record
            result_item = current_rdm_records_service.publish(
                uploader.identity, draft.id
            )
            record = result_item._record
            current_rdm_records_service.indexer.index(
                record, arguments={"refresh": True}
            )

            return record

    return Record()


@pytest.fixture()
def record_factory(db, uploader, minimal_record, community, location):
    """Creates a record that belongs to a community."""

    class RecordFactory:
        """Test record class."""

        def create_record(
            self,
            record_dict=minimal_record,
            uploader=uploader,
            community=community,
            file=None,
        ):
            """Creates new record that belongs to the same community."""
            service = current_rdm_records_service
            files_service = service.draft_files
            idty = uploader.identity
            # create draft
            if file:
                record_dict["files"] = {"enabled": True}
            draft = service.create(idty, record_dict)

            # add file to draft
            if file:
                files_service.init_files(idty, draft.id, data=[{"key": file}])
                files_service.set_file_content(
                    idty, draft.id, file, BytesIO(b"test file")
                )
                files_service.commit_file(idty, draft.id, file)

            # publish and get record
            result_item = service.publish(idty, draft.id)
            record = result_item._record
            if community:
                # add the record to the community
                community_record = community._record
                record.parent.communities.add(community_record, default=False)
                record.parent.commit()
                db.session.commit()
                service.indexer.index(record, arguments={"refresh": True})

            return record

    return RecordFactory()


@pytest.fixture(scope="session")
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need, index_users):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "administration-access")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    index_users()
    return u


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


@pytest.fixture()
def oauth2_client(db, uploader):
    """Create client."""
    with db.session.begin_nested():
        # create resource_owner -> client_1
        client_ = Client(
            client_id="client_test_u1c1",
            client_secret="client_test_u1c1",
            name="client_test_u1c1",
            description="",
            is_confidential=False,
            user_id=uploader.id,
            _redirect_uris="",
            _default_scopes="",
        )
        db.session.add(client_)
    db.session.commit()
    return client_.client_id


@pytest.fixture()
def index_users():
    """Index users for an up-to-date user service."""

    def _index():
        current_users_service.indexer.process_bulk_queue()
        current_users_service.record_cls.index.refresh()

    return _index


@pytest.fixture()
def replace_notification_builder(monkeypatch):
    """Replace a notification builder and return a mock."""

    def _replace(builder_cls):
        mock_build = mock.MagicMock()
        mock_build.side_effect = builder_cls.build
        monkeypatch.setattr(builder_cls, "build", mock_build)
        # setting specific builder for test case
        monkeypatch.setattr(
            current_notifications_manager,
            "builders",
            {
                **current_notifications_manager.builders,
                builder_cls.type: builder_cls,
            },
        )
        return mock_build

    return _replace
