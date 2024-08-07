# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for RecordAccessService."""

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import GrantExistsError


def test_cant_create_multiple_grants_for_same_user(running_app, minimal_record, users):
    """Test that grant for the same record can not be created more than 1 time for a certain user."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant
    user_id = str(users[0].id)
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }

    grant = access_service.bulk_create_grants(
        superuser_identity, record.id, grant_payload
    )

    assert grant.to_dict() == {
        "hits": {
            "hits": [
                {
                    "permission": "preview",
                    "subject": {"id": user_id, "type": "user"},
                    "origin": None,
                    "id": 0,
                }
            ],
            "total": 1,
        }
    }

    # try to create again
    with pytest.raises(GrantExistsError):
        access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)


def test_cant_create_multiple_grants_for_same_role(running_app, minimal_record, roles):
    """Test that grant for the same record can not be created more than 1 time for a certain role."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "role", "id": "test"},
                "permission": "preview",
            }
        ]
    }
    grant = access_service.bulk_create_grants(
        superuser_identity, record.id, grant_payload
    )

    assert grant.to_dict() == {
        "hits": {
            "hits": [
                {
                    "permission": "preview",
                    "subject": {"id": "test", "type": "role"},
                    "origin": None,
                    "id": 0,
                }
            ],
            "total": 1,
        }
    }

    # try to create again
    with pytest.raises(GrantExistsError):
        access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)


def test_create_multiple_grants(running_app, minimal_record, users):
    """Test creating multiple grants at the same time."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grants
    user_id = str(users[0].id)
    user_id2 = str(users[1].id)
    access_service = records_service.access
    grants_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            },
            {
                "subject": {"type": "user", "id": user_id2},
                "permission": "manage",
            },
        ]
    }

    access_service.bulk_create_grants(superuser_identity, record.id, grants_payload)

    read_grants = access_service.read_all_grants(
        superuser_identity,
        record.id,
    )

    assert read_grants.to_dict() == {
        "hits": {
            "hits": [
                {
                    "permission": "preview",
                    "subject": {"id": user_id, "type": "user"},
                    "origin": None,
                    "id": 0,
                },
                {
                    "permission": "manage",
                    "subject": {"id": user_id2, "type": "user"},
                    "origin": None,
                    "id": 1,
                },
            ],
            "total": 2,
        }
    }


def test_create_multiple_grants_one_exists(running_app, minimal_record, users):
    """Test creating multiple grants at the same time. One grant already exists. None added in the end."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant
    user_id = str(users[0].id)
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            },
        ]
    }

    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # create 2 grants, one of them already exists
    user_id2 = str(users[1].id)
    grants_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            },
            {
                "subject": {"type": "user", "id": user_id2},
                "permission": "manage",
            },
        ]
    }

    with pytest.raises(GrantExistsError):
        access_service.bulk_create_grants(superuser_identity, record.id, grants_payload)

    # assert that second grant wasn't added
    grants = access_service.read_all_grants(
        superuser_identity,
        record.id,
    )

    assert grants.to_dict() == {
        "hits": {
            "hits": [
                {
                    "permission": "preview",
                    "subject": {"id": user_id, "type": "user"},
                    "origin": None,
                    "id": 0,
                }
            ],
            "total": 1,
        }
    }


def test_read_grant_by_subjectid_found(running_app, minimal_record, users):
    """Test read grant by user id."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant
    subject_type = "user"
    access_service = records_service.access
    user_id = str(users[0].id)
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # read grant
    grant = access_service.read_grant_by_subject(
        superuser_identity, record.id, user_id, subject_type=subject_type
    )
    assert grant.to_dict() == {
        "permission": "preview",
        "subject": {"id": user_id, "type": "user"},
        "origin": None,
    }


def test_read_grant_by_subjectid_not_found(running_app, minimal_record, users):
    """Test read grant by user id. Not found."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant for user
    subject_type = "user"
    user_id = str(users[0].id)
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # try to read grant for different user
    access_service = records_service.access
    with pytest.raises(LookupError):
        access_service.read_grant_by_subject(
            superuser_identity, record.id, "10000000", subject_type=subject_type
        )


def test_read_grant_by_subjectid_no_grants(running_app, minimal_record, users):
    """Test read grant by user id. No grants."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # try to read grant
    subject_type = "user"
    user_id = str(users[0].id)
    access_service = records_service.access
    with pytest.raises(LookupError):
        access_service.read_grant_by_subject(
            superuser_identity, record.id, user_id, subject_type=subject_type
        )


def test_read_grant_by_subjectid_provide_role(running_app, minimal_record, roles):
    """Test read grant by user id while searching by role"""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant for role "test"
    subject_type = "user"
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "role", "id": "test"},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # try to read grant by role "test"
    access_service = records_service.access
    with pytest.raises(LookupError):
        access_service.read_grant_by_subject(
            superuser_identity, record.id, "test", subject_type=subject_type
        )


def test_delete_grant_by_subjectid_found(running_app, minimal_record, users):
    """Test delete grant by user id."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant
    subject_type = "user"
    access_service = records_service.access
    user_id = str(users[0].id)
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # delete grant
    grant = access_service.delete_grant_by_subject(
        superuser_identity, record.id, user_id, subject_type=subject_type
    )
    assert grant is True

    # try to read grant
    with pytest.raises(LookupError):
        access_service.read_grant_by_subject(
            superuser_identity, record.id, user_id, subject_type=subject_type
        )


def test_delete_grant_by_subjectid_not_found(running_app, minimal_record, users):
    """Test delete grant by user id. Not found."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant for user
    subject_type = "user"
    user_id = str(users[0].id)
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # try to delete grant for different user
    access_service = records_service.access
    with pytest.raises(LookupError):
        access_service.delete_grant_by_subject(
            superuser_identity, record.id, "10000000", subject_type=subject_type
        )


def test_delete_grant_by_subjectid_no_grants(running_app, minimal_record, users):
    """Test delete grant by user id. No grants."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # try to read grant
    subject_type = "user"
    access_service = records_service.access
    with pytest.raises(LookupError):
        access_service.delete_grant_by_subject(
            superuser_identity, record.id, str(users[0].id), subject_type=subject_type
        )


def test_delete_grant_by_subjectid_provide_role(running_app, minimal_record, roles):
    """Test delete grant by user id while searching by role"""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create grant for role "test"
    subject_type = "user"
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "role", "id": "test"},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # try to read grant by role "test"
    access_service = records_service.access
    with pytest.raises(LookupError):
        access_service.delete_grant_by_subject(
            superuser_identity, record.id, "test", subject_type=subject_type
        )


def test_read_all_grants_by_subject_found(running_app, minimal_record, users, roles):
    """Test read user grants."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create user grants
    subject_type = "user"
    access_service = records_service.access
    user_id = str(users[0].id)
    user_id2 = str(users[1].id)
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    grant_payload2 = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id2},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload2)

    # create role grants
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "role", "id": "test"},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # search user grants
    grants = access_service.read_all_grants_by_subject(
        superuser_identity, record.id, subject_type=subject_type
    )
    assert grants.to_dict()["hits"]["total"] == 2
    assert grants.to_dict()["hits"]["hits"][0]["subject"]["type"] == "user"
    assert grants.to_dict()["hits"]["hits"][0]["subject"]["id"] == user_id
    assert grants.to_dict()["hits"]["hits"][1]["subject"]["type"] == "user"
    assert grants.to_dict()["hits"]["hits"][1]["subject"]["id"] == user_id2


def test_read_all_grants_by_subject_not_found(
    running_app, minimal_record, users, roles
):
    """Test read user grants. Not found."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)
    access_service = records_service.access

    # create role grants
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "role", "id": "test"},
                "permission": "preview",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # search user grants
    subject_type = "user"
    grants = access_service.read_all_grants_by_subject(
        superuser_identity, record.id, subject_type=subject_type
    )
    assert grants.to_dict()["hits"]["total"] == 0


def test_update_grant_by_subject_found(running_app, minimal_record, users):
    """Test partial update of user grant."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create user grant
    subject_type = "user"
    access_service = records_service.access
    user_id = str(users[0].id)
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
                "origin": "origin",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # update user grant
    payload = {"permission": "manage"}
    result = access_service.update_grant_by_subject(
        superuser_identity,
        id_=record.id,
        subject_id=user_id,
        subject_type=subject_type,
        data=payload,
    )
    assert result.to_dict()["permission"] == "manage"

    # read grant
    grant = access_service.read_grant_by_subject(
        superuser_identity, record.id, user_id, subject_type=subject_type
    )
    assert grant.to_dict()["permission"] == "manage"


def test_update_grant_by_subject_not_found(running_app, minimal_record, roles):
    """Test partial update of user grant. Not found."""
    # create record
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(superuser_identity, minimal_record)
    record = records_service.publish(superuser_identity, draft.id)

    # create role grant
    access_service = records_service.access
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "role", "id": "test"},
                "permission": "preview",
                "origin": "origin",
            }
        ]
    }
    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # update user grant
    payload = {"permission": "manage"}
    subject_type = "user"
    with pytest.raises(LookupError):
        access_service.update_grant_by_subject(
            superuser_identity,
            id_=record.id,
            subject_id="test",
            subject_type=subject_type,
            data=payload,
        )


def test_update_grant_by_subject_permissions(
    running_app, minimal_record, uploader, users, test_user
):
    """Test permissions when you partially update a user grant."""
    # create record (owner - uploader)
    records_service = current_rdm_records.records_service
    draft = records_service.create(uploader.identity, minimal_record)
    record = records_service.publish(uploader.identity, draft.id)

    # grant manage access to user
    subject_type = "user"
    access_service = records_service.access
    user_with_grant = test_user
    user_with_grant_id = user_with_grant.id
    grant_payload = {
        "grants": [
            {
                "subject": {"type": subject_type, "id": user_with_grant_id},
                "permission": "manage",
                "origin": "origin",
            }
        ]
    }

    access_service.bulk_create_grants(
        running_app.superuser_identity, record.id, grant_payload
    )

    # assert that user can manage record - they can create a new version
    res = records_service.new_version(user_with_grant.identity, id_=record.id)
    assert res.data["versions"]["index"] == 2

    # update user grant - view access
    payload = {"permission": "view"}
    result = access_service.update_grant_by_subject(
        uploader.identity,
        id_=record.id,
        subject_id=user_with_grant_id,
        subject_type=subject_type,
        data=payload,
    )
    assert result.to_dict()["permission"] == "view"

    # assert that now user can not create a new version
    with pytest.raises(PermissionDeniedError):
        records_service.new_version(user_with_grant.identity, id_=record.id)


def test_delete_grant_by_subject_permissions(
    running_app, minimal_record, uploader, users, test_user
):
    """Test permissions when you delete a user grant."""
    # create record (owner - uploader)
    superuser_identity = running_app.superuser_identity
    records_service = current_rdm_records.records_service
    draft = records_service.create(uploader.identity, minimal_record)
    record = records_service.publish(uploader.identity, draft.id)

    # grant manage access to user
    subject_type = "user"
    access_service = records_service.access
    user_with_grant = test_user
    user_with_grant_id = user_with_grant.id
    grant_payload = {
        "grants": [
            {
                "subject": {"type": subject_type, "id": user_with_grant_id},
                "permission": "manage",
                "origin": "origin",
            }
        ]
    }

    access_service.bulk_create_grants(superuser_identity, record.id, grant_payload)

    # assert that user can manage record - they can create a new version
    res = records_service.new_version(user_with_grant.identity, id_=record.id)
    assert res.data["versions"]["index"] == 2

    # delete user grant
    access_service.delete_grant_by_subject(
        superuser_identity, record.id, user_with_grant_id, subject_type=subject_type
    )

    # assert that now user can not create a new version
    with pytest.raises(PermissionDeniedError):
        records_service.new_version(user_with_grant.identity, id_=record.id)
