# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
# Copyright (C) 2021 Northwestern University
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""PID related tests for Invenio RDM Records.

This tests both the PIDsService and the RDMService behaviour related to pids.
"""

from copy import deepcopy

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def mock_public_doi(mocker):
    def public_doi(self, *args, **kwargs):
        # success
        pass

    mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        + "DataCiteRESTClient.public_doi",
        public_doi,
    )


@pytest.fixture()
def mock_hide_doi(mocker):
    def hide_doi(self, *args, **kwargs):
        # success
        pass

    mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        + "DataCiteRESTClient.hide_doi",
        hide_doi,
    )


#
# Reserve & Discard
#


def test_resolve_pid(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    record = service.publish(superuser_identity, draft.id)
    doi = record["pids"]["doi"]["identifier"]

    # test resolution
    resolved_record = service.pids.resolve(
        identity=superuser_identity, id_=doi, scheme="doi"
    )
    assert resolved_record.id == record.id
    assert resolved_record["pids"]["doi"]["identifier"] == doi


def test_resolve_non_existing_pid(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    service.publish(superuser_identity, draft.id)

    # test resolution
    fake_doi = "10.4321/client.12345-abdce"
    with pytest.raises(PIDDoesNotExistError):
        service.pids.resolve(identity=superuser_identity, id_=fake_doi, scheme="doi")


def test_reserve_pid(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    # publish the record
    doi = draft["pids"]["doi"]["identifier"]
    # FIXME: remove all occurences of _ methods, create methods in manager
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.NEW


def test_discard_existing_pid(running_app, search_clear, minimal_record):
    # note discard is only performed over NEW pids for pids in status RESERVED
    # or REGISTERED the invalidate function must be used
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    # publish the record
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.NEW
    draft = service.pids.discard(superuser_identity, draft.id, "doi")
    assert not draft["pids"].get("doi")
    with pytest.raises(PIDDoesNotExistError):
        pid = provider.get(pid_value=doi)


def test_discard_non_exisisting_pid(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    with pytest.raises(PIDDoesNotExistError):
        service.pids.discard(superuser_identity, draft.id, "doi")


def test_oai_pid_default_created(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    record = service.publish(superuser_identity, draft.id)
    published_oai = record.to_dict()["pids"]["oai"]

    assert published_oai["identifier"]
    assert published_oai["provider"] == "oai"
    assert "client" not in published_oai


#
# Workflows
#
#  Use cases list:
#
# | Creation
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Draft creation from scratch (no pid)             | basic_flow                        |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Publish with no pid (creation of mandatory ones) | basic_flow                        |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Do not allow duplicates                          | duplicates                        |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Fail on empty (invalid) value for external pid   | creation_invalid_external_payload |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
#
# | Reservation
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Reserve pid                                      | reserve_managed                   |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Fail to reserve with already existing managed    | reserve_fail_existing_managed     |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Fail to reserve with already existing external   | reserve_fail_existing_external    |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
#
# | Update on drafts (prefix test_pids_drafts)
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from external to managed on a draft       | updates_external_to_managed       |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from external to no pid on a draft        | updates_external_to_managed       |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from managed to external on a draft       | updates_managed_to_external       |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from managed to no pid on a draft         | updates_managed_to_no_pid         |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from no pid to external on a draft        | updates_no_pid_to_external        |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from no pid to managed on a draft         | updates_no_pid_to_managed         |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
#
# | Update on records
# | Note that cases with no function assigned are not testable because doi is mandatory and     # noqa
# | one will always be assinged on publishing.
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from external to managed on a record      | updates_flow_external_to_managed  |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from external to no pid on a record       | updates_flow_external_to_managed  |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from managed to external on a record      | updates_managed_to_external_fail  |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from managed to no pid on a record        | updates_managed_to_no_pid_fail    |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from no pid to external on a record       |                                   |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Update from no pid to managed on a record        |                                   |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
#
# | Publishing
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Publish with a managed pid (from reserve)        | publish_managed                   |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Publish with an external pid                     | publish_external                  |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
#
# | Deletion
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Delete a draft with a managed pid                | delete_managed_pid_from_draft     |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Delete a draft with an external pid              | delete_external_pid_from_draft    |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Delete an edit (draft) with a managed pid        | delete_managed_pid_from_record    |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa
# | Delete an edit (draft) with an external pid      | delete_external_pid_from_record   |  # noqa
# |--------------------------------------------------|-----------------------------------|  # noqa


# Creation


def test_pids_basic_flow(running_app, search_clear, minimal_record, mock_public_doi):
    # external doi and mandatory assignation when empty pids
    # is tested at resources level
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    assert draft["pids"] == {}

    # publish the record with a managed PID
    record = service.publish(superuser_identity, draft.id)
    published_doi = record["pids"]["doi"]
    assert published_doi["identifier"]
    assert published_doi["provider"] == "datacite"  # default
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_doi["identifier"])
    assert pid.status == PIDStatus.REGISTERED  # registration is async


def test_pids_duplicates(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    # create an external pid for an already existing NEW managed one
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]

    data = minimal_record.copy()
    data["pids"]["doi"] = {"identifier": doi, "provider": "external"}

    duplicated_draft = service.create(superuser_identity, data)
    error_msg = {
        "field": "pids.doi",
        "messages": [
            f"doi:{doi} already exists.",
            "The prefix '10.1234' is managed by Invenio. Please supply an external DOI or select 'No' to have a DOI generated for you.",
        ],
    }
    assert error_msg in duplicated_draft.errors

    # create an external pid for an already existing RESERVED managed one
    record = service.publish(superuser_identity, draft.id)

    duplicated_draft = service.create(superuser_identity, data)
    error_msg = {
        "field": "pids.doi",
        "messages": [
            f"doi:{doi} already exists.",
            "The prefix '10.1234' is managed by Invenio. Please supply an external DOI or select 'No' to have a DOI generated for you.",
        ],
    }
    assert error_msg in duplicated_draft.errors

    # create an external pid for an already existing external one
    data = minimal_record.copy()
    doi = "10.4321/test.1234"
    data["pids"]["doi"] = {"identifier": doi, "provider": "external"}
    draft = service.create(superuser_identity, data)
    record = service.publish(superuser_identity, draft.id)

    duplicated_draft = service.create(superuser_identity, data)
    error_msg = {"field": "pids.doi", "messages": [f"doi:{doi} already exists."]}
    assert error_msg in duplicated_draft.errors

    # create a managed pid for an already existing external one
    draft = service.create(superuser_identity, minimal_record)
    doi = draft["pids"]["doi"]["identifier"]
    data = minimal_record.copy()
    data["pids"]["doi"] = {"identifier": doi, "provider": "external"}

    duplicated_draft = service.create(superuser_identity, data)
    error_msg = {"field": "pids.doi", "messages": [f"doi:{doi} already exists."]}
    assert error_msg in duplicated_draft.errors


def test_pids_creation_invalid_external_payload(
    running_app, search_clear, minimal_record
):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service

    data = minimal_record.copy()
    data["pids"]["doi"] = {
        "identifier": "",
        "provider": "external",
    }

    draft = service.create(superuser_identity, data)
    assert draft.errors == [
        {"field": "pids.doi", "messages": ["Missing DOI for required field."]}
    ]


# Reservation


def test_pids_reserve_managed(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # "reserve" pid
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.NEW


def test_pids_reserve_fail_existing_managed(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # "reserve" pid (first assignation)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.NEW
    # reserve again
    with pytest.raises(ValidationError):
        service.pids.create(superuser_identity, draft.id, "doi")


def test_pids_reserve_fail_existing_external(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    data = minimal_record.copy()
    data["pids"]["doi"] = {"identifier": "10.4321/dummy.1234", "provider": "external"}
    draft = service.create(superuser_identity, minimal_record)
    # reserve again
    with pytest.raises(ValidationError):
        service.pids.create(superuser_identity, draft.id, "doi")


# Update on drafts


def test_pids_drafts_updates_external_to_managed(
    running_app, search_clear, minimal_record
):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    data = minimal_record.copy()
    data["pids"]["doi"] = {"identifier": "10.4321/dummy.1234", "provider": "external"}
    draft = service.create(superuser_identity, minimal_record)
    with pytest.raises(PIDDoesNotExistError):  # pid should not exist
        provider.get(
            pid_value=draft["pids"]["doi"]["identifier"], pid_provider="external"
        )

    # remove and reserve a managed one
    draft["pids"].pop("doi")
    draft = service.update_draft(
        id_=draft.id, identity=superuser_identity, data=draft.data
    )
    assert not draft["pids"].get("doi")
    # managed pids needs to first be created (reserve)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    assert provider.get(pid_value=doi).status == PIDStatus.NEW


def test_pids_drafts_updates_managed_to_external(
    running_app, search_clear, minimal_record
):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    assert provider.get(pid_value=doi).status == PIDStatus.NEW

    # remove doi: mandatory delete action, press the X in the UI
    draft = service.pids.discard(superuser_identity, draft.id, "doi")
    # replace by external
    draft["pids"]["doi"] = {"identifier": "10.4321/dummy.1234", "provider": "external"}
    draft = service.update_draft(
        id_=draft.id, identity=superuser_identity, data=draft.data
    )

    assert draft["pids"]["doi"]["identifier"] == "10.4321/dummy.1234"
    assert draft["pids"]["doi"]["provider"] == "external"

    with pytest.raises(PIDDoesNotExistError):  # pid should not exist
        provider.get(
            pid_value=draft["pids"]["doi"]["identifier"], pid_provider="external"
        )

    with pytest.raises(PIDDoesNotExistError):  # original doi was also deleted
        provider.get(pid_value=doi)


def test_pids_drafts_updates_managed_to_no_pid(
    running_app, search_clear, minimal_record
):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    assert provider.get(pid_value=doi).status == PIDStatus.NEW

    # remove doi: mandatory delete action, press the X in the UI
    draft = service.pids.discard(superuser_identity, draft.id, "doi")

    assert not draft["pids"].get("doi")
    with pytest.raises(PIDDoesNotExistError):  # original doi was also deleted
        provider.get(pid_value=doi)


def test_pids_drafts_updates_no_pid_to_external(
    running_app, search_clear, minimal_record
):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    assert draft["pids"] == {}

    # add external
    draft["pids"]["doi"] = {"identifier": "10.4321/dummy.1234", "provider": "external"}
    draft = service.update_draft(
        id_=draft.id, identity=superuser_identity, data=draft.data
    )

    assert draft["pids"]["doi"]["identifier"] == "10.4321/dummy.1234"
    assert draft["pids"]["doi"]["provider"] == "external"

    with pytest.raises(PIDDoesNotExistError):  # pid should not exist
        provider.get(
            pid_value=draft["pids"]["doi"]["identifier"], pid_provider="external"
        )


def test_pids_drafts_updates_no_pid_to_managed(
    running_app, search_clear, minimal_record
):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    assert draft["pids"] == {}

    # add managed
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    assert provider.get(pid_value=doi).status == PIDStatus.NEW


# Update on records
# There is a slight race condition in these tests between assertions and the
# celery task because DOI publish() moves the status from NEW to RESERVED
# synchronously and RESERVED to REGISTERED asynchronously. So
# tests are made to account for that by checking for either RESERVED
# or REGISTERED.


def _create_and_publish_external(service, provider, identity, data):
    """Creates a draft with a managed doi and publishes it."""
    # create the draft
    data["pids"]["doi"] = {"identifier": "10.4321/dummy.1234", "provider": "external"}
    draft = service.create(identity, data)
    # publish and check the doi is in pidstore
    record = service.publish(identity, draft.id)
    pid = provider.get(pid_value="10.4321/dummy.1234")
    assert pid.status == PIDStatus.REGISTERED

    return record


def _create_and_publish_managed(service, provider, identity, data):
    """Creates a draft with a managed doi and publishes it."""
    # create the draft
    draft = service.create(identity, data)
    # "reserve" pid if not given
    draft = service.pids.create(identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.NEW
    # publish and check the doi is in pidstore
    record = service.publish(identity, draft.id)
    pid = provider.get(pid_value=doi)
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]

    return record


def test_pids_records_updates_external_to_managed(
    running_app, search_clear, minimal_record, identity_simple
):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    record = _create_and_publish_external(
        service, provider, superuser_identity, minimal_record
    )

    # create draft
    draft = service.edit(superuser_identity, record.id)
    # remove external pid allowed
    old_doi = draft["pids"].pop("doi")
    draft = service.update_draft(
        id_=draft.id, identity=superuser_identity, data=draft.data
    )
    assert not draft["pids"].get("doi")

    # add a new managed doi
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.NEW

    # publish with managed doi
    record = service.publish(superuser_identity, draft.id)
    pid = provider.get(pid_value=doi)
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]
    # the old external should be completely deleted
    with pytest.raises(PIDDoesNotExistError):
        provider.get(pid_value=old_doi["identifier"], pid_provider=old_doi["provider"])


def test_pids_records_updates_managed_to_external_fail(
    running_app,
    search_clear,
    minimal_record,
    identity_simple,
    mock_hide_doi,
):
    service = current_rdm_records.records_service
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    record = _create_and_publish_managed(
        service, provider, identity_simple, minimal_record
    )

    # create draft
    draft = service.edit(identity_simple, record.id)
    # fail to remove doi due to lack of permissions (validation error)
    with pytest.raises(ValidationError):
        service.pids.discard(identity_simple, draft.id, "doi")

    doi = draft["pids"]["doi"]["identifier"]
    assert doi
    pid = provider.get(pid_value=doi)
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]


def test_pids_records_updates_managed_to_no_pid_fail(
    running_app, search_clear, minimal_record, identity_simple
):
    service = current_rdm_records.records_service
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    record = _create_and_publish_managed(
        service, provider, identity_simple, minimal_record
    )

    # create draft
    draft = service.edit(identity_simple, record.id)
    # fail to remove doi due to lack of permissions (validation error)
    with pytest.raises(ValidationError):
        service.pids.discard(identity_simple, draft.id, "doi")

    doi = draft["pids"]["doi"]["identifier"]
    assert doi
    pid = provider.get(pid_value=doi)
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]


# Publishing


def test_pids_publish_managed(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    assert provider.get(pid_value=doi).status == PIDStatus.NEW

    # publish
    record = service.publish(superuser_identity, draft.id)
    # registration is async
    pid = provider.get(pid_value=doi)
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]


def test_pids_publish_external(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create the draft
    data = minimal_record.copy()
    data["pids"]["doi"] = {"identifier": "10.4321/dummy.1234", "provider": "external"}
    draft = service.create(superuser_identity, data)
    with pytest.raises(PIDDoesNotExistError):  # pid should not exist
        provider.get(
            pid_value=draft["pids"]["doi"]["identifier"], pid_provider="external"
        )

    # publish
    record = service.publish(superuser_identity, draft.id)
    pid = provider.get(
        pid_value=record["pids"]["doi"]["identifier"], pid_provider="external"
    )
    assert pid.pid_value == record["pids"]["doi"]["identifier"]
    # registration is async
    assert pid.status == PIDStatus.REGISTERED


# Deletion


def test_pids_delete_external_pid_from_draft(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create draft
    data = minimal_record.copy()
    data["pids"] = {"doi": {"identifier": "10.4321/dummy.1234", "provider": "external"}}
    draft = service.create(superuser_identity, data)

    # delete draft
    assert service.delete_draft(superuser_identity, draft.id)
    with pytest.raises(PIDDoesNotExistError):  # pid should not exist
        provider.get(
            pid_value=data["pids"]["doi"]["identifier"], pid_provider="external"
        )


def test_pids_delete_managed_pid_from_draft(running_app, search_clear, minimal_record):
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create draft and doi
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    pid = provider.get(pid_value=draft["pids"]["doi"]["identifier"])
    assert pid.status == PIDStatus.NEW
    assert pid.pid_value == draft["pids"]["doi"]["identifier"]

    # delete draft
    assert service.delete_draft(superuser_identity, draft.id)
    with pytest.raises(PIDDoesNotExistError):  # pid should not exist
        provider.get(pid_value=pid.pid_value, pid_provider="external")


def test_pids_delete_external_pid_from_record(
    running_app, search_clear, minimal_record
):
    # This test aims to delete from a draft created out of a published record
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create draft
    data = minimal_record.copy()
    data["pids"] = {"doi": {"identifier": "10.4321/dummy.1234", "provider": "external"}}
    draft = service.create(superuser_identity, data)
    # publish
    record = service.publish(superuser_identity, draft.id)
    pid = provider.get(
        pid_value=record["pids"]["doi"]["identifier"],
        pid_provider=record["pids"]["doi"]["provider"],
    )
    assert pid.status == PIDStatus.REGISTERED
    assert pid.pid_value == record["pids"]["doi"]["identifier"]
    # create new draft
    draft = service.edit(superuser_identity, record.id)
    pid = provider.get(
        pid_value=draft["pids"]["doi"]["identifier"],
        pid_provider=draft["pids"]["doi"]["provider"],
    )
    assert pid.status == PIDStatus.REGISTERED
    assert pid.pid_value == draft["pids"]["doi"]["identifier"]
    # delete draft (should not delete pid since it is part of an active record)
    assert service.delete_draft(superuser_identity, draft.id)
    pid = provider.get(
        pid_value=record["pids"]["doi"]["identifier"],
        pid_provider=record["pids"]["doi"]["provider"],
    )
    assert pid.status == PIDStatus.REGISTERED
    assert pid.pid_value == record["pids"]["doi"]["identifier"]


def test_pids_delete_managed_pid_from_record(running_app, search_clear, minimal_record):
    # This test aims to delete from a draft created out of a published record
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    provider = service.pids.pid_manager._get_provider("doi", "datacite")

    # create draft and managed doi
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")

    # publish
    record = service.publish(superuser_identity, draft.id)
    pid = provider.get(pid_value=record["pids"]["doi"]["identifier"])
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]
    assert pid.pid_value == record["pids"]["doi"]["identifier"]

    # create new draft
    draft = service.edit(superuser_identity, record.id)
    pid = provider.get(pid_value=draft["pids"]["doi"]["identifier"])
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]
    assert pid.pid_value == draft["pids"]["doi"]["identifier"]

    # delete draft (should not delete pid since it is part of an active record)
    assert service.delete_draft(superuser_identity, draft.id)
    pid = provider.get(pid_value=record["pids"]["doi"]["identifier"])
    assert pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]
    assert pid.pid_value == record["pids"]["doi"]["identifier"]


#
# Versioning
#


def test_pids_versioning(running_app, search_clear, minimal_record, mock_public_doi):
    """Test PIDs for multi-versioned records."""
    # new version + publish
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}

    # create draft
    draft = service.create(superuser_identity, minimal_record)
    assert draft["pids"] == {}
    assert draft["parent"]["pids"] == {}

    # publish the record with a managed PID
    record = service.publish(superuser_identity, draft.id)
    parent = record._record.parent

    # parent doi + doi
    published_doi_v1 = record["pids"]["doi"]
    assert published_doi_v1["identifier"] == f"10.1234/{record.id}"
    assert published_doi_v1["provider"] == "datacite"
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_doi_v1["identifier"])
    assert pid.status == PIDStatus.REGISTERED

    published_parent_doi = record["parent"]["pids"]["doi"]
    assert published_parent_doi["identifier"] == f"10.1234/{parent.pid.pid_value}"
    assert published_parent_doi["provider"] == "datacite"
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_parent_doi["identifier"])
    assert pid.status == PIDStatus.REGISTERED

    # create new version
    draft = service.new_version(superuser_identity, record.id)
    draft_data = deepcopy(draft.data)
    draft_data["metadata"]["publication_date"] = "2023-01-01"
    draft = service.update_draft(superuser_identity, draft.id, data=draft_data)
    record_v2 = service.publish(superuser_identity, draft.id)
    parent = record_v2._record.parent

    # new version doi
    published_doi_v2 = record_v2["pids"]["doi"]
    assert published_doi_v2["identifier"] == f"10.1234/{record_v2.id}"
    assert published_doi_v2["provider"] == "datacite"
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_doi_v2["identifier"])
    assert pid.status == PIDStatus.REGISTERED

    # parent doi should be the same
    published_parent_doi = record_v2["parent"]["pids"]["doi"]
    assert published_parent_doi["identifier"] == f"10.1234/{parent.pid.pid_value}"
    assert published_parent_doi["provider"] == "datacite"
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_parent_doi["identifier"])
    assert pid.status == PIDStatus.REGISTERED


def test_pids_versioning_external_doi(
    running_app, search_clear, minimal_record, mock_public_doi
):
    """Test PIDs for multi-versioned records with external DOI."""
    # new version + publish
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}

    # create draft with external DOI
    data = minimal_record.copy()
    data["pids"]["doi"] = {"identifier": "10.4321/external.v1", "provider": "external"}

    draft = service.create(superuser_identity, data)
    assert draft["pids"] == {
        "doi": {"identifier": "10.4321/external.v1", "provider": "external"},
    }
    assert draft["parent"]["pids"] == {}

    # publish the record with an external DOI
    record = service.publish(superuser_identity, draft.id)
    parent = record._record.parent

    # external doi only
    published_doi_v1 = record["pids"]["doi"]
    assert published_doi_v1["identifier"] == "10.4321/external.v1"
    assert published_doi_v1["provider"] == "external"
    provider = service.pids.pid_manager._get_provider("doi", "external")
    pid = provider.get(pid_value=published_doi_v1["identifier"])
    assert pid.status == PIDStatus.REGISTERED

    # parent doi shouldn't be registered when publishing external doi
    assert "doi" not in record["parent"]["pids"]

    # create new version with managed doi
    draft = service.new_version(superuser_identity, record.id)
    draft_data = deepcopy(draft.data)
    draft_data["metadata"]["publication_date"] = "2023-01-01"
    draft_data["pids"] = {}  # unset, so that we get a managed doi
    draft = service.update_draft(superuser_identity, draft.id, data=draft_data)
    record_v2 = service.publish(superuser_identity, draft.id)
    parent = record_v2._record.parent

    # new version managed doi + parent doi (since we have a managed doi now)
    published_doi_v2 = record_v2["pids"]["doi"]
    assert published_doi_v2["identifier"] == f"10.1234/{record_v2.id}"
    assert published_doi_v2["provider"] == "datacite"
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_doi_v2["identifier"])
    assert pid.status == PIDStatus.REGISTERED

    # parent doi should be now present
    published_parent_doi = record_v2["parent"]["pids"]["doi"]
    assert published_parent_doi["identifier"] == f"10.1234/{parent.pid.pid_value}"
    assert published_parent_doi["provider"] == "datacite"
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=published_parent_doi["identifier"])
    assert pid.status == PIDStatus.REGISTERED
