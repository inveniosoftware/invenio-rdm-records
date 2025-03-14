# # -*- coding: utf-8 -*-
# #
# # Copyright (C) 2023-2024 CERN.
# # Copyright (C) 2023 TU Wien.
# #
# # Invenio-RDM is free software; you can redistribute it and/or modify
# # it under the terms of the MIT License; see LICENSE file for more details.
"""Test user moderation actions."""

import pytest
from celery import Task
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_requests.proxies import (
    current_requests_service,
    current_user_moderation_service,
)

from invenio_rdm_records.proxies import current_rdm_records_service as records_service


class MockRequestModerationTask(Task):
    """Mock celery task for moderation request."""

    def apply_async(self, args=None, kwargs=None, **kwargs_):
        user_id = kwargs["user_id"]
        try:
            current_user_moderation_service.request_moderation(
                system_identity, user_id=user_id, uow=None
            )
        except Exception as ex:
            pass


def test_user_moderation_approve(
    running_app, mod_identity, unverified_user, es_clear, minimal_record, mocker
):
    """Tests moderation action after user approval.

    The user records, and all its versions, should have a "is_verified" field set to "True".
    """

    user_records_q = f"parent.access.owned_by.user:{unverified_user.id}"

    # Create a record
    draft = records_service.create(unverified_user.identity, minimal_record)
    record = records_service.publish(id_=draft.id, identity=unverified_user.identity)

    # Create a new version of the record
    new_version = records_service.new_version(unverified_user.identity, id_=record.id)
    records_service.update_draft(
        unverified_user.identity, new_version.id, minimal_record
    )
    # Since tasks are executed synchronously in tests, the db session used for publishing is rolledback.
    # This is a patch for tests only.
    mocker.patch(
        "invenio_rdm_records.services.components.verified.request_moderation",
        MockRequestModerationTask(),
    )
    new_record = records_service.publish(
        identity=unverified_user.identity, id_=new_version.id
    )

    pre_approval_records = records_service.search(
        system_identity, params={"q": user_records_q, "allversions": True}
    )

    assert pre_approval_records.total == 2
    hits = pre_approval_records.to_dict()["hits"]["hits"]
    is_verified = all([hit["parent"]["is_verified"] for hit in hits])

    assert is_verified is False

    # Fetch moderation request that was created on publish
    res = current_requests_service.search(
        system_identity, params={"q": f"topic.user:{unverified_user.id}"}
    )
    assert res.total == 1

    mod_request = res.to_dict()["hits"]["hits"][0]

    # Approve user, records are verified from now on
    current_requests_service.execute_action(
        mod_identity, id_=mod_request["id"], action="accept"
    )

    # Records are re-indexed in bulk. We need to force it for tests, otherwise it's done by a celery beat task
    records_service.indexer.process_bulk_queue()
    records_service.record_cls.index.refresh()

    post_approval_records = records_service.search(
        system_identity, params={"q": user_records_q, "allversions": True}
    )

    assert post_approval_records.total == 2
    hits = post_approval_records.to_dict()["hits"]["hits"]
    is_verified = all([hit["parent"]["is_verified"] for hit in hits])
    assert is_verified is True


def test_user_moderation_decline(
    running_app, mod_identity, unverified_user, es_clear, minimal_record, mocker
):
    """Tests user moderation action after decline.

    All of the user's records should be deleted.
    """
    # Create a record
    draft = records_service.create(unverified_user.identity, minimal_record)
    record = records_service.publish(id_=draft.id, identity=unverified_user.identity)
    assert not record._record.deletion_status.is_deleted
    assert record._record.tombstone is None

    # Fetch moderation request that was created on publish and decline the user
    res = current_requests_service.search(
        system_identity, params={"q": f"topic.user:{unverified_user.id}"}
    )
    assert res.total == 1
    mod_request = res.to_dict()["hits"]["hits"][0]
    current_requests_service.execute_action(
        mod_identity, id_=mod_request["id"], action="decline"
    )

    # The user's record should now be deleted
    record = records_service.read(
        id_=draft.id, identity=system_identity, include_deleted=True
    )
    assert record._record.deletion_status.is_deleted
    assert record._record.tombstone is not None


def test_is_verified_system_user(running_app, minimal_record):
    """Test is_verified when create is system user."""
    draft = records_service.create(system_identity, minimal_record)
    record = records_service.publish(id_=draft.id, identity=system_identity)
    parent_dict = record.to_dict()["parent"]
    assert parent_dict["access"]["owned_by"]["user"] == system_identity.id
    assert parent_dict["is_verified"]
