# # -*- coding: utf-8 -*-
# #
# # Copyright (C) 2023 CERN.
# #
# # Invenio-RDM is free software; you can redistribute it and/or modify
# # it under the terms of the MIT License; see LICENSE file for more details.
"""Test user moderation actions."""

from invenio_access.permissions import system_identity
from invenio_requests.proxies import current_requests_service

from invenio_rdm_records.proxies import current_rdm_records_service as records_service


def fetch_user_records(user_id, allversions=False):
    """Fetches records from a given user."""
    user_records_q = f"parent.access.owned_by.user:{user_id}"
    return records_service.search(
        system_identity, params={"q": user_records_q, "allversions": allversions}
    )


def test_user_moderation_approve(
    running_app,
    mod_request_create,
    mod_identity,
    uploader,
    test_user,
    es_clear,
    minimal_record,
):
    """Tests moderation action after user approval.

    The user records, and all its versions, should have a "is_verified" field set to "True".
    """
    # Create a record
    draft = records_service.create(uploader.identity, minimal_record)
    record = records_service.publish(id_=draft.id, identity=uploader.identity)

    # Create a new version of the record
    new_version = records_service.new_version(uploader.identity, id_=record.id)
    records_service.update_draft(uploader.identity, new_version.id, minimal_record)
    new_record = records_service.publish(identity=uploader.identity, id_=new_version.id)

    pre_approval_records = fetch_user_records(uploader.id, allversions=True)
    assert pre_approval_records.total == 2
    hits = pre_approval_records.to_dict()["hits"]["hits"]
    is_verified = all([hit["parent"]["is_verified"] for hit in hits])

    assert is_verified == False

    moderation_request = mod_request_create(uploader.id)

    # Approve user, records are verified from now on
    current_requests_service.execute_action(
        mod_identity, id_=moderation_request.id, action="accept"
    )

    post_approval_records = fetch_user_records(uploader.id, allversions=True)
    assert post_approval_records.total == 2
    hits = post_approval_records.to_dict()["hits"]["hits"]
    is_verified = all([hit["parent"]["is_verified"] for hit in hits])
    assert is_verified == True
