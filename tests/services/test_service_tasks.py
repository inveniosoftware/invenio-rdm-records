# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service tasks tests."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.services.tasks import update_expired_embargos


def test_embargo_lift_without_draft(embargoed_files_record, running_app, search_clear):
    update_expired_embargos()

    service = current_rdm_records.records_service
    record_lifted = service.record_cls.pid.resolve(embargoed_files_record["id"])
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
    RDMDraft.index.refresh()

    update_expired_embargos()

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
    RDMDraft.index.refresh()

    update_expired_embargos()

    record_lifted = service.record_cls.pid.resolve(record["id"])
    draft_lifted = service.draft_cls.pid.resolve(ongoing_draft["id"])

    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == "public"
    assert record_lifted.access.protection.record == "public"

    assert draft_lifted.access.embargo.active is False
    assert draft_lifted.access.protection.files == "restricted"
    assert draft_lifted.access.protection.record == "public"
