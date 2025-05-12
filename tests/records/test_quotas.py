# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


from invenio_access.permissions import system_identity
from invenio_db import db

from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.records.models import RDMRecordQuota, RDMUserQuota


def test_user_quota(app, identity_simple, minimal_record, location, resource_type_v):
    """Test the effectiveness of ``RDMUserQuota`` for new drafts."""
    quota = (
        db.session.query(RDMUserQuota)
        .filter(RDMUserQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is None

    old_draft = records_service.create(identity_simple, minimal_record)._obj
    assert old_draft.bucket.quota_size == 1000000
    assert old_draft.bucket.max_file_size == 1000000

    # Set the user quota and see if new drafts are affected
    records_service.set_user_quota(
        system_identity, identity_simple.id, {"quota_size": 1337, "max_file_size": 420}
    )
    quota = (
        db.session.query(RDMUserQuota)
        .filter(RDMUserQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is not None
    assert quota.user_id == identity_simple.id
    assert quota.quota_size == 1337
    assert quota.max_file_size == 420

    draft = records_service.create(identity_simple, minimal_record)._obj
    assert draft.bucket.quota_size == 1337
    assert draft.bucket.max_file_size == 420

    # But old drafts shouldn't be affected
    draft = records_service.read_draft(identity_simple, old_draft.pid.pid_value)._obj
    assert draft.bucket.quota_size == 1000000
    assert draft.bucket.max_file_size == 1000000


def test_record_quota(app, identity_simple, minimal_record, location, resource_type_v):
    """Test the effectiveness of ``RDMRecordQuota``."""
    quota = (
        db.session.query(RDMRecordQuota)
        .filter(RDMRecordQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is None

    draft = records_service.create(identity_simple, minimal_record)._obj
    assert draft.bucket.quota_size == 1000000
    assert draft.bucket.max_file_size == 1000000

    # Set the record quota and see if it affected the existing draft
    records_service.set_quota(
        system_identity, draft.pid.pid_value, {"quota_size": 1337, "max_file_size": 420}
    )
    quota = (
        db.session.query(RDMRecordQuota)
        .filter(RDMRecordQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is not None
    assert quota.user_id == identity_simple.id
    assert quota.quota_size == 1337
    assert quota.max_file_size == 420

    draft = records_service.read_draft(identity_simple, draft.pid.pid_value)._obj
    assert draft.bucket.quota_size == 1337
    assert draft.bucket.max_file_size == 420

    # Check that a new version of the draft still has the same quota
    records_service.publish(identity_simple, draft.pid.pid_value)
    draft = records_service.new_version(identity_simple, draft.pid.pid_value)._obj
    assert draft.bucket.quota_size == 1337
    assert draft.bucket.max_file_size == 420
