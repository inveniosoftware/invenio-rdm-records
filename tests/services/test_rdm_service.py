# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
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


#
# Embargo lift
#
def test_embargo_lift_without_draft(embargoed_record, running_app, search_clear):
    record = embargoed_record
    service = current_rdm_records.records_service

    service.lift_embargo(_id=record["id"], identity=running_app.superuser_identity)

    record_lifted = service.record_cls.pid.resolve(record["id"])
    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == "public"
    assert record_lifted.access.protection.record == "public"
    assert record_lifted.access.status.value == "metadata-only"


def test_embargo_lift_with_draft(embargoed_record, search_clear, superuser_identity):
    record = embargoed_record
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
    embargoed_record, superuser_identity, search_clear
):
    record = embargoed_record
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
