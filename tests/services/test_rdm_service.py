# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Service level tests for Invenio RDM Records."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import EmbargoNotLiftedError


def test_minimal_draft_creation(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service

    record_item = service.create(superuser_identity, minimal_record)
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["resource_type"] == {
        "id": "image-photo",
        "title": {"en": "Photo"},
    }


def test_draft_w_languages_creation(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["metadata"]["languages"] = [
        {
            "id": "eng",
        }
    ]

    record_item = service.create(superuser_identity, minimal_record)
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["languages"] == [
        {"id": "eng", "title": {"en": "English", "da": "Engelsk"}}
    ]


# Test restricted record with doi creation


def test_publish_public_record_with_default_doi(
    running_app, search_clear, minimal_record
):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)
    assert "doi" in record._record.pids


def test_publish_public_record_with_optional_doi(
    running_app, search_clear, minimal_record
):
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["required"] = False
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)
    assert "doi" not in record._record.pids
    # Reset the running_app config for next tests
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["required"] = True


def test_publish_restricted_record_without_default_doi(
    running_app, search_clear, minimal_restricted_record
):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_restricted_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)
    assert (
        "doi" not in record._record.pids
    )  # Restricted records do not create by default a doi


def test_publish_restricted_record_with_external_doi(
    running_app, search_clear, minimal_restricted_record
):
    superuser_identity = running_app.superuser_identity
    minimal_restricted_record["pids"]["doi"] = {
        "identifier": "10.1235/rdm.5678",
        "provider": "external",
    }
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_restricted_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)
    assert "doi" in record._record.pids
    assert record._record.pids["doi"]["identifier"] == "10.1235/rdm.5678"
    assert record._record.pids["doi"]["provider"] == "external"


def test_embargo_lift_creates_doi(running_app, search_clear, embargoed_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    assert "doi" not in embargoed_record._record.pids
    service.lift_embargo(_id=embargoed_record["id"], identity=superuser_identity)
    record_lifted = service.record_cls.pid.resolve(embargoed_record["id"])
    assert "doi" in record_lifted.pids


def test_public_record_to_restricted_keeps_doi(
    running_app, search_clear, minimal_record
):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)
    assert "doi" in record._record.pids

    draft = service.edit(superuser_identity, record.id)
    draft["access"]["record"] = "restricted"
    draft = service.update_draft(superuser_identity, draft.id, draft.data)
    record = service.publish(superuser_identity, draft.id)
    assert "doi" in record._record.pids


#
# Embargo lift
#
def test_embargo_lift_without_draft(embargoed_files_record, running_app, search_clear):
    record = embargoed_files_record
    service = current_rdm_records.records_service

    service.lift_embargo(_id=record["id"], identity=running_app.superuser_identity)

    record_lifted = service.record_cls.pid.resolve(record["id"])
    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == "public"
    assert record_lifted.access.protection.record == "public"
    assert record_lifted.access.status.value == "metadata-only"


def test_embargo_lift_with_draft(
    embargoed_files_record, search_clear, superuser_identity
):
    record = embargoed_files_record
    service = current_rdm_records.records_service

    # Edit a draft
    ongoing_draft = service.edit(id_=record["id"], identity=superuser_identity)

    service.lift_embargo(_id=record["id"], identity=superuser_identity)
    record_lifted = service.record_cls.pid.resolve(record["id"])
    draft_lifted = service.draft_cls.pid.resolve(ongoing_draft["id"])

    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == "public"
    assert record_lifted.access.protection.record == "public"

    assert draft_lifted.access.embargo.active is False
    assert draft_lifted.access.protection.files == "public"
    assert draft_lifted.access.protection.record == "public"


def test_embargo_lift_with_updated_draft(
    embargoed_files_record, superuser_identity, search_clear
):
    record = embargoed_files_record
    service = current_rdm_records.records_service

    # This draft simulates an existing one while lifting the record
    draft = service.edit(id_=record["id"], identity=superuser_identity).data

    # Change record's title and access field to be restricted
    draft["metadata"]["title"] = "Record modified by the user"
    draft["access"]["status"] = "restricted"
    draft["access"]["embargo"] = dict(active=False, until=None, reason=None)
    # Update the ongoing draft with the new data simulating the user's input
    ongoing_draft = service.update_draft(
        id_=draft["id"], identity=superuser_identity, data=draft
    )

    service.lift_embargo(_id=record["id"], identity=superuser_identity)
    record_lifted = service.record_cls.pid.resolve(record["id"])
    draft_lifted = service.draft_cls.pid.resolve(ongoing_draft["id"])

    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == "public"
    assert record_lifted.access.protection.record == "public"

    assert draft_lifted.access.embargo.active is False
    assert draft_lifted.access.protection.files == "restricted"
    assert draft_lifted.access.protection.record == "public"


def test_embargo_lift_with_error(running_app, search_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    # Add embargo to record
    minimal_record["access"]["files"] = "restricted"
    minimal_record["access"]["status"] = "embargoed"
    minimal_record["access"]["embargo"] = dict(
        active=True, until="3220-06-01", reason=None
    )
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)

    # Record should not be lifted since it didn't expire (until 3220)
    with pytest.raises(EmbargoNotLiftedError):
        service.lift_embargo(_id=record["id"], identity=superuser_identity)


def test_search_sort_verified_enabled(
    running_app,
    minimal_record,
    search_clear,
    monkeypatch,
    verified_user,
    unverified_user,
):
    """Tests sort by 'is_verified' field, when enabled.

    The flag "RDM_SEARCH_SORT_BY_VERIFIED" is monkeypatched (only modified for this test).
    """
    service = current_rdm_records.records_service

    # NV : non-verified
    nv_user = unverified_user
    # V  : verified
    v_user = verified_user

    # Create two records for two distinct users (verified record is published first)
    v_draft = service.create(v_user.identity, minimal_record)
    assert v_draft
    v_record = service.publish(id_=v_draft.id, identity=v_user.identity)
    assert v_record

    nv_draft = service.create(nv_user.identity, minimal_record)
    assert nv_draft
    nv_record = service.publish(id_=nv_draft.id, identity=nv_user.identity)
    assert nv_record

    # Disable sort by 'verified' and sort by 'latest': unverified record will be the first
    monkeypatch.setitem(running_app.app.config, "RDM_SEARCH_SORT_BY_VERIFIED", False)
    res = service.search(nv_user.identity, sort="newest")
    assert res.total == 2
    hits = res.to_dict()["hits"]["hits"]

    expected_order = [nv_record.id, v_record.id]
    assert expected_order == [h["id"] for h in hits]

    # Enable sort by 'verified' and sort by 'latest': unverified record will be the last
    monkeypatch.setitem(running_app.app.config, "RDM_SEARCH_SORT_BY_VERIFIED", True)
    res = service.search(nv_user.identity, sort="newest")
    assert res.total == 2
    hits = res.to_dict()["hits"]["hits"]

    expected_order = [v_record.id, nv_record.id]
    assert expected_order == [h["id"] for h in hits]
