# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN
# Copyright (C) 2024 Graz University of Technology.
# Copyright (C) 2025-2026 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""PID service tasks tests."""

from copy import deepcopy
from unittest import mock

import pytest
from invenio_i18n import _
from invenio_pidstore.models import PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.resources.serializers import CrossrefXMLSerializer
from invenio_rdm_records.services.pids import providers
from invenio_rdm_records.services.pids.tasks import register_or_update_pid


@pytest.fixture()
def crossref_config(running_app, mock_crossref_client):
    old_config = running_app.app.config.copy()
    running_app.app.config.update(
        {
            "CROSSREF_ENABLED": True,
            "DATACITE_ENABLED": False,
            "CROSSREF_USERNAME": "INVALID",
            "CROSSREF_PASSWORD": "INVALID",
            "CROSSREF_DEPOSITOR": "INVALID",
            "CROSSREF_EMAIL": "info@example.org",
            "CROSSREF_REGISTRANT": "INVALID",
            "CROSSREF_PREFIX": "10.1234",
            "RDM_PERSISTENT_IDENTIFIER_PROVIDERS": [
                providers.CrossrefPIDProvider(
                    "crossref",
                    client=mock_crossref_client,
                    label=_("DOI"),
                ),
                # DOI provider for externally managed DOIs
                providers.ExternalPIDProvider(
                    "external",
                    "doi",
                    validators=[
                        providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])
                    ],
                    label=_("DOI"),
                ),
                # OAI identifier
                providers.OAIPIDProvider(
                    "oai",
                    label=_("OAI ID"),
                ),
            ],
            "RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS": [
                providers.CrossrefPIDProvider(
                    "crossref",
                    client=mock_crossref_client,
                    serializer=CrossrefXMLSerializer(
                        schema_context={"is_parent": True}
                    ),
                    label=_("Concept DOI"),
                ),
            ],
        }
    )
    yield
    running_app.app.config.clear()
    running_app.app.config.update(old_config)


@pytest.fixture(scope="module")
def mock_datacite_client(mock_datacite_client):
    """Mock DataCite client API calls."""
    with mock.patch.object(mock_datacite_client, "api"):
        yield mock_datacite_client


@pytest.fixture(scope="module")
def mock_crossref_client(mock_crossref_client):
    """Mock Crossref client API calls."""

    def generate_doi(record, **kwargs):
        return "10.1234/mock.doi"

    def deposit(*args, **kwargs):
        return None

    def cfg(key):
        # Gibt einen Dummy-Wert für alle Konfigurationsschlüssel zurück
        return f"mock_{key}"

    mock_crossref_client.generate_doi = generate_doi
    mock_crossref_client.deposit = mock.Mock(side_effect=deposit)
    mock_crossref_client.name = "crossref"
    mock_crossref_client.cfg = cfg
    yield mock_crossref_client


def test_register_pid(
    running_app,
    search_clear,
    minimal_record,
    superuser_identity,
    mock_datacite_client,
):
    """Registers a PID."""
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "datacite"}}
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED
    mock_datacite_client.api.public_doi.assert_has_calls(
        [
            mock.call(
                metadata={
                    "identifiers": [{"identifier": doi, "identifierType": "DOI"}],
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "publisher": "Acme Inc",
                    "creators": [
                        {
                            "givenName": "Troy",
                            "nameIdentifiers": [],
                            "familyName": "Brown",
                            "nameType": "Personal",
                            "name": "Brown, Troy",
                        },
                        {
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                            "name": "Troy Inc.",
                        },
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "publicationYear": "2020",
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                },
                url=f"https://127.0.0.1:5000/doi/{doi}",
                doi=doi,
            )
        ]
    )


def test_register_pid_crossref(
    running_app,
    search_clear,
    minimal_record,
    superuser_identity,
    mock_crossref_client,
    crossref_config,
):
    """Registers a Crossref DOI."""
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["providers"] = [
        "crossref",
        "external",
    ]
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["is_enabled"] = (
        lambda *args, **kwargs: True
    )
    service = current_rdm_records.records_service
    data = minimal_record.copy()
    doi = "10.1234/test.1234"
    data["pids"]["doi"] = {
        "identifier": doi,
        "provider": "crossref",
        "client": "crossref",
    }
    draft = service.create(superuser_identity, data)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "crossref")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "crossref"}}
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED
    mock_crossref_client.api.post.assert_has_calls(
        [
            mock.call(
                metadata={
                    "identifiers": [{"identifier": doi, "identifierType": "DOI"}],
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "publisher": "Acme Inc",
                    "creators": [
                        {
                            "givenName": "Troy",
                            "nameIdentifiers": [],
                            "familyName": "Brown",
                            "nameType": "Personal",
                            "name": "Brown, Troy",
                        },
                        {
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                            "name": "Troy Inc.",
                        },
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "publicationYear": "2020",
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                },
                url=f"https://127.0.0.1:5000/doi/{doi}",
                doi=doi,
            )
        ]
    )


def test_register_restricted_pid(
    running_app,
    search_clear,
    minimal_record,
    superuser_identity,
    mock_datacite_client,
):
    """Test register restricted pid."""
    minimal_record["access"]["record"] = "restricted"
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "datacite"}}
    record.metadata = draft["metadata"]
    record.access = draft["access"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status != PIDStatus.REGISTERED
    mock_datacite_client.api.public_doi.assert_has_calls([])
    mock_datacite_client.api.draft_doi.assert_has_calls([])

    access = draft["access"]
    access["record"] = "public"
    record.access = access
    record.commit()
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED
    mock_datacite_client.api.public_doi.assert_has_calls(
        [
            mock.call(
                metadata={
                    "identifiers": [{"identifier": doi, "identifierType": "DOI"}],
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "publisher": "Acme Inc",
                    "creators": [
                        {
                            "givenName": "Troy",
                            "nameIdentifiers": [],
                            "familyName": "Brown",
                            "nameType": "Personal",
                            "name": "Brown, Troy",
                        },
                        {
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                            "name": "Troy Inc.",
                        },
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "publicationYear": "2020",
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                },
                url=f"https://127.0.0.1:5000/doi/{doi}",
                doi=doi,
            )
        ]
    )


def test_update_pid(
    running_app,
    search_clear,
    minimal_record,
    mocker,
    superuser_identity,
    mock_datacite_client,
):
    """No pid provided, creating one by default."""
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    # oai = record["pids"]["oai"]["identifier"]  # entfernt, da ungenutzt
    doi = record["pids"]["doi"]["identifier"]
    parent_doi = record["parent"]["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    parent_provider = service.pids.parent_pid_manager._get_provider("doi", "datacite")
    parent_pid = parent_provider.get(pid_value=parent_doi)
    assert parent_pid.status == PIDStatus.REGISTERED

    # we do not explicitly call the update_pid task
    # we check that the lower level provider update is called
    record_edited = service.edit(superuser_identity, record.id)
    assert mock_datacite_client.api.update_doi.called is False
    service.publish(superuser_identity, record_edited.id)

    mock_datacite_client.api.update_doi.assert_has_calls(
        [
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "name": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": parent_doi,
                            "relationType": "IsVersionOf",
                            "relatedIdentifierType": "DOI",
                        }
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": doi, "identifierType": "DOI"},
                        {
                            "identifier": record["pids"]["oai"]["identifier"],
                            "identifierType": "oai",
                        },
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=doi,
                url=f"https://127.0.0.1:5000/doi/{doi}",
            ),
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "name": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": doi,
                            "relationType": "HasVersion",
                            "relatedIdentifierType": "DOI",
                        }
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": parent_doi, "identifierType": "DOI"}
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=parent_doi,
                url=f"https://127.0.0.1:5000/doi/{parent_doi}",
            ),
        ],
        any_order=True,
    )


def test_update_pid_crossref(
    running_app,
    search_clear,
    minimal_record,
    mocker,
    superuser_identity,
    mock_crossref_client,
    crossref_config,
):
    """No pid provided, creating one by default."""
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["providers"] = [
        "crossref",
        "external",
    ]
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["is_enabled"] = (
        lambda *args, **kwargs: True
    )
    minimal_record["pids"]["doi"] = {
        "identifier": "10.1234/inveniordm.1234",
        "provider": "crossref",
        "client": "crossref",
    }
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    # oai = record["pids"]["oai"]["identifier"]  # entfernt, da ungenutzt
    doi = record["pids"]["doi"]["identifier"]
    parent_doi = record["parent"]["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "crossref")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    parent_provider = service.pids.parent_pid_manager._get_provider("doi", "crossref")
    parent_pid = parent_provider.get(pid_value=parent_doi)
    assert parent_pid.status == PIDStatus.REGISTERED

    # we do not explicitly call the update_pid task
    # we check that the lower level provider update is called
    record_edited = service.edit(superuser_identity, record.id)
    assert mock_crossref_client.deposit.called is False
    service.publish(superuser_identity, record_edited.id)

    mock_crossref_client.deposit.assert_has_calls(
        [
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "name": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": parent_doi,
                            "relationType": "IsVersionOf",
                            "relatedIdentifierType": "DOI",
                        }
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": doi, "identifierType": "DOI"},
                        {
                            "identifier": record["pids"]["oai"]["identifier"],
                            "identifierType": "oai",
                        },
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=doi,
                url=f"https://127.0.0.1:5000/doi/{doi}",
            ),
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "name": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": doi,
                            "relationType": "HasVersion",
                            "relatedIdentifierType": "DOI",
                        }
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": parent_doi, "identifierType": "DOI"}
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=parent_doi,
                url=f"https://127.0.0.1:5000/doi/{parent_doi}",
            ),
        ],
        any_order=True,
    )


def test_invalidate_pid(
    running_app,
    search_clear,
    minimal_record,
    mocker,
    superuser_identity,
    mock_datacite_client,
):
    """No pid provided, creating one by default."""
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    # oai = record["pids"]["oai"]["identifier"]  # entfernt, da ungenutzt
    doi = record["pids"]["doi"]["identifier"]
    parent_doi = record["parent"]["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    parent_provider = service.pids.parent_pid_manager._get_provider("doi", "datacite")
    parent_pid = parent_provider.get(pid_value=parent_doi)
    assert parent_pid.status == PIDStatus.REGISTERED

    tombstone_info = {"note": "no specific reason, tbh"}

    record = service.delete_record(
        superuser_identity, id_=record.id, data=tombstone_info
    )

    assert mock_datacite_client.api.hide_doi.called is True
    assert mock_datacite_client.api.update_doi.called is True
    mock_datacite_client.api.update_doi.assert_has_calls(
        [
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "familyName": "Troy Inc.",
                            "name": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": parent_doi, "identifierType": "DOI"}
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=parent_doi,
                url=f"https://127.0.0.1:5000/doi/{parent_doi}",
            ),
        ]
    )

    # make sure we still have the PID registered for tombstone
    assert record._record.pid.status == PIDStatus.REGISTERED


def test_invalidate_versions_pid(
    running_app,
    search_clear,
    minimal_record,
    mocker,
    superuser_identity,
    mock_datacite_client,
):
    """No pid provided, creating one by default."""
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    # oai = record["pids"]["oai"]["identifier"]  # not used
    doi = record["pids"]["doi"]["identifier"]
    parent_doi = record["parent"]["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    parent_provider = service.pids.parent_pid_manager._get_provider("doi", "datacite")
    parent_pid = parent_provider.get(pid_value=parent_doi)
    assert parent_pid.status == PIDStatus.REGISTERED

    minimal_record_v2 = deepcopy(minimal_record)
    minimal_record_v2["metadata"]["title"] = f"{minimal_record['metadata']['title']} v2"
    draft_v2 = service.new_version(superuser_identity, record.id)
    service.update_draft(superuser_identity, draft_v2.id, minimal_record_v2)
    record_v2 = service.publish(superuser_identity, draft_v2.id)
    record_v2_doi = record_v2["pids"]["doi"]["identifier"]

    tombstone_info = {"note": "no specific reason, tbh"}

    # delete v1
    record = service.delete_record(
        superuser_identity, id_=record.id, data=tombstone_info
    )

    assert mock_datacite_client.api.hide_doi.called is True
    assert mock_datacite_client.api.update_doi.called is True

    expected_calls = [
        # UPDATE PARENT WITH BOTH VERSIONS (publish new)
        mock.call(
            metadata={
                "event": "publish",
                "schemaVersion": "http://datacite.org/schema/kernel-4",
                "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                "creators": [
                    {
                        "name": "Brown, Troy",
                        "familyName": "Brown",
                        "nameIdentifiers": [],
                        "nameType": "Personal",
                        "givenName": "Troy",
                    },
                    {
                        "name": "Troy Inc.",
                        "nameIdentifiers": [],
                        "nameType": "Organizational",
                    },
                ],
                "relatedIdentifiers": [
                    {
                        "relatedIdentifier": record_v2_doi,
                        "relationType": "HasVersion",
                        "relatedIdentifierType": "DOI",
                    },
                    {
                        "relatedIdentifier": doi,
                        "relationType": "HasVersion",
                        "relatedIdentifierType": "DOI",
                    },
                ],
                "titles": [{"title": "A Romans story v2"}],
                "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                "identifiers": [{"identifier": parent_doi, "identifierType": "DOI"}],
                "publicationYear": "2020",
                "publisher": "Acme Inc",
            },
            doi=parent_doi,
            url=f"https://127.0.0.1:5000/doi/{parent_doi}",
        ),
        # REMOVE ONE VERSION FROM THE PARENT
        mock.call(
            metadata={
                "event": "publish",
                "schemaVersion": "http://datacite.org/schema/kernel-4",
                "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                "creators": [
                    {
                        "name": "Brown, Troy",
                        "familyName": "Brown",
                        "nameIdentifiers": [],
                        "nameType": "Personal",
                        "givenName": "Troy",
                    },
                    {
                        "name": "Troy Inc.",
                        "nameIdentifiers": [],
                        "nameType": "Organizational",
                    },
                ],
                "relatedIdentifiers": [
                    {
                        "relatedIdentifier": record_v2_doi,
                        "relationType": "HasVersion",
                        "relatedIdentifierType": "DOI",
                    }
                ],
                "titles": [{"title": "A Romans story v2"}],
                "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                "identifiers": [
                    {"identifier": parent_doi, "identifierType": "DOI"},
                ],
                "publicationYear": "2020",
                "publisher": "Acme Inc",
            },
            doi=parent_doi,
            url=f"https://127.0.0.1:5000/doi/{parent_doi}",
        ),
    ]

    mock_datacite_client.api.update_doi.assert_has_calls(expected_calls)

    # make sure we still have the PID registered for tombstone
    assert record._record.pid.status == PIDStatus.REGISTERED

    # DELETE THE SECOND VERSION
    service.delete_record(
        superuser_identity, id_=record_v2.id, data=tombstone_info
    )  # record_v2_del entfernt, da ungenutzt

    mock_datacite_client.api.update_doi.assert_has_calls(
        expected_calls
        + [
            # REMOVE LAST VERSION FROM THE PARENT
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "name": "Troy Inc.",
                            "familyName": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "titles": [{"title": "A Romans story v2"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": parent_doi, "identifierType": "DOI"},
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=parent_doi,
                url=f"https://127.0.0.1:5000/doi/{parent_doi}",
            ),
        ],
    )


def test_restore_pid(
    running_app,
    search_clear,
    minimal_record,
    mocker,
    superuser_identity,
    mock_datacite_client,
):
    """No pid provided, creating one by default."""
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    # oai = record["pids"]["oai"]["identifier"]  # entfernt, da ungenutzt
    doi = record["pids"]["doi"]["identifier"]
    parent_doi = record["parent"]["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    parent_provider = service.pids.parent_pid_manager._get_provider("doi", "datacite")
    parent_pid = parent_provider.get(pid_value=parent_doi)
    assert parent_pid.status == PIDStatus.REGISTERED

    tombstone_info = {"note": "no specific reason, tbh"}

    record = service.delete_record(
        superuser_identity, id_=record.id, data=tombstone_info
    )

    assert mock_datacite_client.api.hide_doi.called is True
    assert mock_datacite_client.api.update_doi.called is True

    expected_calls = [
        mock.call(
            metadata={
                "event": "publish",
                "schemaVersion": "http://datacite.org/schema/kernel-4",
                "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                "creators": [
                    {
                        "name": "Brown, Troy",
                        "familyName": "Brown",
                        "nameIdentifiers": [],
                        "nameType": "Personal",
                        "givenName": "Troy",
                    },
                    {
                        "familyName": "Troy Inc.",
                        "name": "Troy Inc.",
                        "nameIdentifiers": [],
                        "nameType": "Organizational",
                    },
                ],
                "titles": [{"title": "A Romans story"}],
                "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                "identifiers": [{"identifier": parent_doi, "identifierType": "DOI"}],
                "publicationYear": "2020",
                "publisher": "Acme Inc",
            },
            doi=parent_doi,
            url=f"https://127.0.0.1:5000/doi/{parent_doi}",
        ),
    ]
    mock_datacite_client.api.update_doi.assert_has_calls(expected_calls)

    # make sure we still have the PID registered for tombstone
    assert record._record.pid.status == PIDStatus.REGISTERED

    restored_rec = service.restore_record(superuser_identity, record.id)

    # once for parent + once for the record
    assert mock_datacite_client.api.show_doi.call_count == 2

    mock_datacite_client.api.update_doi.assert_has_calls(
        expected_calls
        + [
            mock.call(
                metadata={
                    "event": "publish",
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
                    "creators": [
                        {
                            "name": "Brown, Troy",
                            "familyName": "Brown",
                            "nameIdentifiers": [],
                            "nameType": "Personal",
                            "givenName": "Troy",
                        },
                        {
                            "name": "Troy Inc.",
                            "familyName": "Troy Inc.",
                            "nameIdentifiers": [],
                            "nameType": "Organizational",
                        },
                    ],
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": doi,  # restored version DOI
                            "relationType": "HasVersion",
                            "relatedIdentifierType": "DOI",
                        },
                    ],
                    "titles": [{"title": "A Romans story"}],
                    "dates": [{"date": "2020-06-01", "dateType": "Issued"}],
                    "identifiers": [
                        {"identifier": parent_doi, "identifierType": "DOI"}
                    ],
                    "publicationYear": "2020",
                    "publisher": "Acme Inc",
                },
                doi=parent_doi,
                url=f"https://127.0.0.1:5000/doi/{parent_doi}",
            ),
        ]
    )

    assert restored_rec._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED


def test_full_record_register(
    running_app,
    search_clear,
    full_record,
    superuser_identity,
    mock_datacite_client,
):
    """Registers a PID for a full record."""
    full_record["pids"] = {}

    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, full_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "datacite"}}
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED

    mock_datacite_client.api.public_doi.assert_has_calls(
        [
            mock.call(
                metadata={
                    "contributors": [
                        {
                            "affiliation": [
                                {
                                    "affiliationIdentifier": "https://ror.org/01ggx4157",
                                    "affiliationIdentifierScheme": "ROR",
                                    "name": "CERN",
                                }
                            ],
                            "contributorType": "Other",
                            "familyName": "Nielsen",
                            "givenName": "Lars Holm",
                            "name": "Nielsen, Lars Holm",
                            "nameIdentifiers": [
                                {
                                    "nameIdentifier": "0000-0001-8135-3489",
                                    "nameIdentifierScheme": "ORCID",
                                }
                            ],
                            "nameType": "Personal",
                        }
                    ],
                    "creators": [
                        {
                            "affiliation": [
                                {
                                    "affiliationIdentifier": "https://ror.org/01ggx4157",
                                    "affiliationIdentifierScheme": "ROR",
                                    "name": "CERN",
                                },
                                {"name": "free-text"},
                            ],
                            "familyName": "Nielsen",
                            "givenName": "Lars Holm",
                            "name": "Nielsen, Lars Holm",
                            "nameIdentifiers": [
                                {
                                    "nameIdentifier": "0000-0001-8135-3489",
                                    "nameIdentifierScheme": "ORCID",
                                }
                            ],
                            "nameType": "Personal",
                        }
                    ],
                    "dates": [
                        {"date": "2018/2020-09", "dateType": "Issued"},
                        {
                            "date": "1939/1945",
                            "dateInformation": "A date",
                            "dateType": "Other",
                        },
                    ],
                    "descriptions": [
                        {
                            "description": "A description \nwith HTML tags",
                            "descriptionType": "Abstract",
                        },
                        {
                            "description": "Bla bla bla",
                            "descriptionType": "Methods",
                            "lang": "eng",
                        },
                    ],
                    "formats": ["application/pdf"],
                    "fundingReferences": [
                        {
                            "awardNumber": "755021",
                            "awardTitle": "Personalised Treatment For "
                            "Cystic Fibrosis Patients "
                            "With Ultra-rare CFTR "
                            "Mutations (and beyond)",
                            "awardURI": "https://cordis.europa.eu/project/id/755021",
                            "funderIdentifier": "00k4n6c32",
                            "funderIdentifierType": "ROR",
                            "funderName": "European Commission",
                        }
                    ],
                    "geoLocations": [
                        {
                            "geoLocationPlace": "test location place",
                            "geoLocationPoint": {
                                "pointLatitude": "-60.63932",
                                "pointLongitude": "-32.94682",
                            },
                        }
                    ],
                    "identifiers": [
                        {
                            "identifier": doi,
                            "identifierType": "DOI",
                        },
                        {
                            "identifier": "1924MNRAS..84..308E",
                            "identifierType": "bibcode",
                        },
                    ],
                    "language": "dan",
                    "publicationYear": "2018",
                    "publisher": "InvenioRDM",
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": "10.1234/foo.bar",
                            "relatedIdentifierType": "DOI",
                            "relationType": "IsCitedBy",
                            "resourceTypeGeneral": "Dataset",
                        }
                    ],
                    "rightsList": [
                        {
                            "rights": "A custom license",
                            "rightsUri": "https://customlicense.org/licenses/by/4.0/",
                        },
                        {
                            "rights": "Creative Commons Attribution 4.0 International",
                            "rightsIdentifier": "cc-by-4.0",
                            "rightsIdentifierScheme": "spdx",
                            "rightsUri": "https://creativecommons.org/licenses/by/4.0/legalcode",
                        },
                    ],
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "sizes": ["11 pages"],
                    "subjects": [
                        {
                            "subject": "Abdominal Injuries",
                            "subjectScheme": "MeSH",
                            "valueURI": "http://id.nlm.nih.gov/mesh/A-D000007",
                        },
                        {"subject": "custom"},
                    ],
                    "titles": [
                        {"title": "InvenioRDM"},
                        {
                            "lang": "eng",
                            "title": "a research data management platform",
                            "titleType": "Subtitle",
                        },
                    ],
                    "types": {
                        "resourceType": "Photo",
                        "resourceTypeGeneral": "Image",
                    },
                    "version": "v1.0",
                },
                url=f"https://127.0.0.1:5000/doi/{doi}",
                doi=doi,
            )
        ]
    )


def test_full_record_register_crossref(
    running_app,
    search_clear,
    full_record,
    superuser_identity,
    mock_crossref_client,
    crossref_config,
):
    """Registers a PID for a full record."""
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["providers"] = [
        "crossref",
        "external",
    ]
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["is_enabled"] = (
        lambda *args, **kwargs: True
    )
    full_record["pids"]["doi"] = {
        "identifier": "10.1234/mock.doi",
        "provider": "crossref",
        "client": "crossref",
    }
    # full_record["metadata"]["resource_type"]["id"] = "publication-preprint"

    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, full_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "crossref")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "crossref"}}
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED

    mock_crossref_client.deposit.assert_has_calls(
        [
            mock.call(
                metadata={
                    "contributors": [
                        {
                            "affiliation": [
                                {
                                    "affiliationIdentifier": "https://ror.org/01ggx4157",
                                    "affiliationIdentifierScheme": "ROR",
                                    "name": "CERN",
                                }
                            ],
                            "contributorType": "Other",
                            "familyName": "Nielsen",
                            "givenName": "Lars Holm",
                            "name": "Nielsen, Lars Holm",
                            "nameIdentifiers": [
                                {
                                    "nameIdentifier": "0000-0001-8135-3489",
                                    "nameIdentifierScheme": "ORCID",
                                }
                            ],
                            "nameType": "Personal",
                        }
                    ],
                    "creators": [
                        {
                            "affiliation": [
                                {
                                    "affiliationIdentifier": "https://ror.org/01ggx4157",
                                    "affiliationIdentifierScheme": "ROR",
                                    "name": "CERN",
                                },
                                {"name": "free-text"},
                            ],
                            "familyName": "Nielsen",
                            "givenName": "Lars Holm",
                            "name": "Nielsen, Lars Holm",
                            "nameIdentifiers": [
                                {
                                    "nameIdentifier": "0000-0001-8135-3489",
                                    "nameIdentifierScheme": "ORCID",
                                }
                            ],
                            "nameType": "Personal",
                        }
                    ],
                    "dates": [
                        {"date": "2018/2020-09", "dateType": "Issued"},
                        {
                            "date": "1939/1945",
                            "dateInformation": "A date",
                            "dateType": "Other",
                        },
                    ],
                    "descriptions": [
                        {
                            "description": "A description \nwith HTML tags",
                            "descriptionType": "Abstract",
                        },
                        {
                            "description": "Bla bla bla",
                            "descriptionType": "Methods",
                            "lang": "eng",
                        },
                    ],
                    "formats": ["application/pdf"],
                    "fundingReferences": [
                        {
                            "awardNumber": "755021",
                            "awardTitle": "Personalised Treatment For "
                            "Cystic Fibrosis Patients "
                            "With Ultra-rare CFTR "
                            "Mutations (and beyond)",
                            "awardURI": "https://cordis.europa.eu/project/id/755021",
                            "funderIdentifier": "00k4n6c32",
                            "funderIdentifierType": "ROR",
                            "funderName": "European Commission",
                        }
                    ],
                    "geoLocations": [
                        {
                            "geoLocationPlace": "test location place",
                            "geoLocationPoint": {
                                "pointLatitude": "-60.63932",
                                "pointLongitude": "-32.94682",
                            },
                        }
                    ],
                    "identifiers": [
                        {
                            "identifier": doi,
                            "identifierType": "DOI",
                        },
                        {
                            "identifier": "1924MNRAS..84..308E",
                            "identifierType": "bibcode",
                        },
                    ],
                    "language": "dan",
                    "publicationYear": "2018",
                    "publisher": "InvenioRDM",
                    "relatedIdentifiers": [
                        {
                            "relatedIdentifier": "10.1234/foo.bar",
                            "relatedIdentifierType": "DOI",
                            "relationType": "IsCitedBy",
                            "resourceTypeGeneral": "Dataset",
                        }
                    ],
                    "rightsList": [
                        {
                            "rights": "A custom license",
                            "rightsUri": "https://customlicense.org/licenses/by/4.0/",
                        },
                        {
                            "rights": "Creative Commons Attribution 4.0 International",
                            "rightsIdentifier": "cc-by-4.0",
                            "rightsIdentifierScheme": "spdx",
                            "rightsUri": "https://creativecommons.org/licenses/by/4.0/legalcode",
                        },
                    ],
                    "schemaVersion": "http://datacite.org/schema/kernel-4",
                    "sizes": ["11 pages"],
                    "subjects": [
                        {
                            "subject": "Abdominal Injuries",
                            "subjectScheme": "MeSH",
                            "valueURI": "http://id.nlm.nih.gov/mesh/A-D000007",
                        },
                        {"subject": "custom"},
                    ],
                    "titles": [
                        {"title": "InvenioRDM"},
                        {
                            "lang": "eng",
                            "title": "a research data management platform",
                            "titleType": "Subtitle",
                        },
                    ],
                    "types": {
                        "resourceType": "Photo",
                        "resourceTypeGeneral": "Image",
                    },
                    "version": "v1.0",
                },
                url=f"https://127.0.0.1:5000/doi/{doi}",
                doi=doi,
            )
        ]
    )
