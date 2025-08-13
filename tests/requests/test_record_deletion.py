# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test user moderation actions."""

from types import SimpleNamespace

import pytest
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_requests.proxies import current_requests_service
from marshmallow import ValidationError

from invenio_rdm_records.requests import RecordDeletion


def _get_owner_identity(record):
    """Get user identity."""
    user = record.parent.access.owned_by.resolve()
    identity = get_identity(user)
    return identity


@pytest.fixture(scope="function")
def deletion_vocabulary():
    """Fixture to mock vocabulary service."""
    return SimpleNamespace(
        **{"data": {"title": {"en": "Test Reason"}}, "id": "test-reason"}
    )


@pytest.fixture(scope="function")
def created_deletion_request(
    minimal_record,
    record_factory,
):
    """Fixture to create a deletion request."""
    record = record_factory.create_record(minimal_record)

    identity = _get_owner_identity(record)

    data = {
        "comment": "Please delete this record.",
        "reason": "test-record",
    }

    request = current_requests_service.create(
        system_identity,
        request_type=RecordDeletion,
        topic=record,
        creator=identity.user,
        receiver=None,
        data={"payload": data},
    )._record

    return request


@pytest.fixture(scope="function")
def submitted_deletion_request(created_deletion_request, deletion_vocabulary, mocker):
    """Fixture to create a submitted deletion request."""
    record = created_deletion_request.topic.resolve()
    identity = _get_owner_identity(record)
    with mocker.patch(
        "invenio_rdm_records.requests.record_deletion.current_vocabularies_service.read",
        return_value=deletion_vocabulary,
    ):
        request = current_requests_service.execute_action(
            identity,
            created_deletion_request.id,
            "submit",
        )._record

    return request


def test_request_create(
    minimal_record,
    record_factory,
):
    """Tests record deleteion request creation."""
    record = record_factory.create_record(minimal_record)

    identity = _get_owner_identity(record)

    data = {
        "comment": "Please delete this record.",
        "reason": "test-record",
    }

    request = current_requests_service.create(
        system_identity,
        request_type=RecordDeletion,
        topic=record,
        creator=identity.user,
        receiver=None,
        data={"payload": data},
    )._record

    record = request.topic.resolve()
    assert request.status == "created"


def test_request_create_exisiting_open_request(
    submitted_deletion_request,
):
    """Tests record deleteion request creation when there is an exisiting open request."""
    record = submitted_deletion_request.topic.resolve()
    identity = _get_owner_identity(record)

    data = {
        "comment": "Please delete this record.",
        "reason": "test-record",
    }

    with pytest.raises(ValidationError):
        current_requests_service.create(
            system_identity,
            request_type=RecordDeletion,
            topic=record,
            creator=identity.user,
            receiver=None,
            data={"payload": data},
        )


def test_request_submit(created_deletion_request, mocker, deletion_vocabulary):
    """Tests record deleteion request submit action."""
    record = created_deletion_request.topic.resolve()
    identity = _get_owner_identity(record)
    with mocker.patch(
        "invenio_rdm_records.requests.record_deletion.current_vocabularies_service.read",
        return_value=deletion_vocabulary,
    ):
        request = current_requests_service.execute_action(
            identity,
            str(created_deletion_request.id),
            "submit",
        )._record

    record = request.topic.resolve()
    assert record.is_deleted is False
    assert request.status == "submitted"


def test_request_accept(submitted_deletion_request, mocker):
    """Tests record deleteion request accept action."""
    delete_patch = mocker.patch(
        "invenio_rdm_records.proxies.current_rdm_records_service.delete_record"
    )
    request = current_requests_service.execute_action(
        system_identity,
        submitted_deletion_request.id,
        "accept",
    )._record

    delete_patch.assert_called_once()
    assert request.status == "accepted"
