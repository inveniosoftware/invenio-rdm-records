# SPDX-FileCopyrightText: 2023 TU Wien.
# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Testing the workflow for access requests."""

import copy
import io
import re
import urllib

import pytest
from flask_principal import UserNeed
from flask_security import login_user
from invenio_access.permissions import (
    Identity,
    any_user,
    authenticated_user,
    system_identity,
)
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.proxies import current_requests_service

from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_rdm_records.requests.access import AccessRequestTokenNeed


def _identity(user):
    """Build a fully-provisioned identity for a user."""
    identity = Identity(user.id)
    identity.provides.add(any_user)
    identity.provides.add(authenticated_user)
    identity.provides.add(UserNeed(user.id))
    return identity


def _create_public_record_restricted_files(identity, minimal_record):
    record_json = copy.deepcopy(minimal_record)
    record_json["files"] = {"enabled": True}
    record_json["access"]["record"] = "public"
    record_json["access"]["files"] = "restricted"

    draft = service.create(identity=identity, data=record_json)
    service.draft_files.init_files(identity, draft.id, data=[{"key": "test.txt"}])
    service.draft_files.set_file_content(
        identity, draft.id, "test.txt", io.BytesIO(b"test file")
    )
    service.draft_files.commit_file(identity, draft.id, "test.txt")
    record = service.publish(identity=identity, id_=draft.id)
    return record


def _grant_permission(record_id, user_id, permission):
    """Grant a given access on a record to a user."""
    service.access.bulk_create_grants(
        identity=system_identity,
        id_=record_id,
        data={
            "grants": [
                {
                    "subject": {"type": "user", "id": str(user_id)},
                    "permission": permission,
                }
            ]
        },
    )


def test_simple_guest_access_request_flow(running_app, client, users, minimal_record):
    """Test a simple guest-based access request flow."""
    with running_app.app.extensions["mail"].record_messages() as outbox:
        # Log in a user (whose ID we need later)
        record_owner, _ = users
        identity = _identity(record_owner)
        guest_identity = Identity(None)
        guest_identity.provides.add(any_user)

        # Create a public record with some restricted files
        record = _create_public_record_restricted_files(identity, minimal_record)

        # Make sure there is no secret link for the record yet
        assert not record._obj.parent.access.links

        # The user can access the record, but not the files
        assert client.get(f"/records/{record.id}").status_code == 200
        assert client.get(f"/records/{record.id}/files").status_code == 403
        assert (
            client.get(f"/records/{record.id}/files/test.txt/content").status_code
            == 403
        )

        # The guest creates an access request
        response = client.post(
            f"/records/{record.id}/access/request",
            json={
                "message": "This is not spam!",
                "email": "idle@montypython.com",
                "full_name": "Eric Idle",
                "consent_to_share_personal_data": "true",
            },
        )
        assert response.status_code == 200
        assert len(outbox) == 1
        verify_email_message = outbox[0]

        # Fetch the link from the response & parse the access request token
        link_regex = re.compile(r"(https?://.*?)\s?$")
        match = link_regex.search(str(verify_email_message.body))
        assert match
        verification_url = match.group(1)
        parsed = urllib.parse.urlparse(verification_url)
        args = {k: v for k, v in [kv.split("=") for kv in parsed.query.split("&")]}
        assert "access_request_token" in args
        token = args["access_request_token"]
        guest_identity.provides.add(AccessRequestTokenNeed(token))

        # Create the access request from the token
        # NOTE: we're not going through a `ui_app.test_client` here because that would
        #       require us to build the frontend assets to get a `manifest.json`
        request = service.access.create_guest_access_request(
            identity=guest_identity, token=args["access_request_token"]
        )

        assert f"/access/requests/{request.id}" in request.links["self_html"]
        assert len(outbox) == 3
        owner_submit_message = outbox[1]
        assert (
            "New access request for your record 'A Romans story'"
            in owner_submit_message.subject
        )

        guest_submit_message = outbox[2]
        assert (
            "Your access request was submitted successfully"
            in guest_submit_message.subject
        )
        assert request["links"]["self_html"] in guest_submit_message.html
        # Following is a 1-off test of invenio_url_for in Jinja settings + dynamic
        # blueprint route registration (decorator style within a function). Good to keep
        # as a smoke test.
        assert (
            "https://127.0.0.1:5000/account/settings/notifications"
            in guest_submit_message.html
        )

        # Accept the request
        # This is expected to send out another email, containing the new secret link
        current_requests_service.execute_action(identity, request.id, "accept", data={})
        assert len(outbox) == 4
        success_message = outbox[3]
        match = link_regex.search(str(success_message.body))
        assert match
        access_url = match.group(1)
        parsed = urllib.parse.urlparse(access_url)
        args = {k: v for k, v in [kv.split("=") for kv in parsed.query.split("&")]}
        assert "token" in args

        # The user can now access the record and its files via the secret link
        assert (
            client.get(f"/records/{record.id}?token={args['token']}").status_code == 200
        )
        assert (
            client.get(f"/records/{record.id}/files?token={args['token']}").status_code
            == 200
        )
        assert (
            client.get(
                f"/records/{record.id}/files/test.txt/content?token={args['token']}"
            ).status_code
            == 200
        )

        # Make sure that the secret link for the record was created
        record = service.read(identity=identity, id_=record.id)
        secret_links = record._obj.parent.access.links
        assert len(secret_links) == 1
        secret_link = secret_links[0].resolve()
        assert secret_link.token == args["token"]
        assert secret_link.permission_level == "view"
        assert secret_link.origin == f"request:{request.id}"


def test_simple_user_access_request_flow(running_app, client, users, minimal_record):
    """Test a simple user-based access request flow."""

    with running_app.app.extensions["mail"].record_messages() as outbox:
        # Log in a user (whose ID we need later)
        record_owner, user = users
        identity = _identity(record_owner)
        login_user(user)
        login_user_via_session(client, email=user.email)

        # Create a public record with some restricted files
        record = _create_public_record_restricted_files(identity, minimal_record)

        # There's no access grants in the record yet
        assert not record._obj.parent.access.grants

        # The user can access the record, but not the files
        assert client.get(f"/records/{record.id}").status_code == 200
        assert client.get(f"/records/{record.id}/files").status_code == 403
        assert (
            client.get(f"/records/{record.id}/files/test.txt/content").status_code
            == 403
        )

        # The user creates an access request
        response = client.post(
            f"/records/{record.id}/access/request",
            json={
                "message": "Please give me access!",
                "email": user.email,
                "full_name": "ABC",
            },
        )
        assert response.status_code == 200
        request_id = response.json["id"]
        assert f"/me/requests/{request_id}" in response.json["links"]["self_html"]
        assert len(outbox) == 1
        submit_message = outbox[0]
        assert response.json["links"]["self_html"] in submit_message.html

        # The record owner approves the access request
        current_requests_service.execute_action(identity, request_id, "accept", data={})
        assert len(outbox) == 2
        success_message = outbox[1]
        assert record.to_dict()["links"]["self_html"] in success_message.body

        # Now, the user has permission to view the record's files!
        assert client.get(f"/records/{record.id}").status_code == 200
        assert client.get(f"/records/{record.id}/files").status_code == 200
        assert (
            client.get(f"/records/{record.id}/files/test.txt/content").status_code
            == 200
        )

        # Verify the created access grant
        record = service.read(identity=identity, id_=record.id)
        grants = record._record.parent.access.grants
        assert len(grants) == 1
        assert grants[0].to_dict() == {
            "subject": {"type": "user", "id": str(user.id)},
            "permission": "view",
            "origin": f"request:{request_id}",
        }


def test_access_grant_for_user(
    running_app,
    client,
    users,
    minimal_restricted_record,
):
    """Test whether we can grant access to specific users."""
    # Log in a user (whose ID we need later)
    user = users[-1]
    login_user(user)
    login_user_via_session(client, email=user.email)

    # Create a restricted record
    draft = service.create(identity=system_identity, data=minimal_restricted_record)
    record = service.publish(identity=system_identity, id_=draft.id)

    response = client.get(f"/records/{record.id}")
    assert response.status_code == 403

    # Grant access to the *current user*
    service.access.bulk_create_grants(
        identity=system_identity,
        id_=record.id,
        data={
            "grants": [
                {
                    "subject": {
                        "type": "user",
                        "id": str(user.id),
                    },
                    "permission": "view",
                }
            ]
        },
    )

    response = client.get(f"/records/{record.id}")
    assert response.status_code == 200


def test_access_grant_for_system_role(
    running_app,
    client_with_login,
    minimal_restricted_record,
):
    """Test whether we can grant access permissions to groups of users."""
    # Create a restricted record
    draft = service.create(identity=system_identity, data=minimal_restricted_record)
    record = service.publish(identity=system_identity, id_=draft.id)

    response = client_with_login.get(f"/records/{record.id}")
    assert response.status_code == 403

    # Grant access to *any authenticated user*
    service.access.bulk_create_grants(
        identity=system_identity,
        id_=record.id,
        data={
            "grants": [
                {
                    "subject": {
                        "type": "system_role",
                        "id": "authenticated_user",
                    },
                    "permission": "view",
                }
            ]
        },
    )

    response = client_with_login.get(f"/records/{record.id}")
    assert response.status_code == 200


def test_manager_can_accept_guest_access_request(
    running_app, client, users, minimal_record
):
    """A user with manage grant can accept a guest access request, but an editor cannot."""
    with running_app.app.extensions["mail"].record_messages() as outbox:
        record_owner, manager = users
        owner_identity = _identity(record_owner)
        manager_identity = _identity(manager)
        guest_identity = Identity(None)
        guest_identity.provides.add(any_user)

        record = _create_public_record_restricted_files(owner_identity, minimal_record)

        # Create a third user as editor
        datastore = running_app.app.extensions["security"].datastore
        editor = datastore.create_user(
            email="editor@example.com", password="password", active=True
        )
        db.session.commit()
        editor_identity = _identity(editor)

        # Grant permissions
        _grant_permission(record.id, manager.id, "manage")
        _grant_permission(record.id, editor.id, "edit")

        # Guest submits an access request
        response = client.post(
            f"/records/{record.id}/access/request",
            json={
                "message": "Please let me in!",
                "email": "guest@example.com",
                "full_name": "Guest User",
                "consent_to_share_personal_data": "true",
            },
        )
        assert response.status_code == 200

        # Parse the verification token from the email
        link_regex = re.compile(r"(https?://.*?)\s?$")
        match = link_regex.search(str(outbox[0].body))
        assert match
        parsed = urllib.parse.urlparse(match.group(1))
        args = {k: v for k, v in [kv.split("=") for kv in parsed.query.split("&")]}
        token = args["access_request_token"]
        guest_identity.provides.add(AccessRequestTokenNeed(token))

        request = service.access.create_guest_access_request(
            identity=guest_identity, token=token
        )

        # Editor cannot read the request
        with pytest.raises(PermissionDeniedError):
            current_requests_service.read(editor_identity, request.id)

        # Editor cannot accept the request
        with pytest.raises(PermissionDeniedError):
            current_requests_service.execute_action(
                editor_identity, request.id, "accept", data={}
            )

        # The manager accepts the request
        current_requests_service.execute_action(
            manager_identity, request.id, "accept", data={}
        )

        result = current_requests_service.read(system_identity, request.id)
        assert result["status"] == "accepted"

        # Get secret link
        success_message = outbox[-1]
        match = link_regex.search(str(success_message.body))
        assert match
        access_url = match.group(1)
        parsed = urllib.parse.urlparse(access_url)
        args = {k: v for k, v in [kv.split("=") for kv in parsed.query.split("&")]}
        assert "token" in args

        # Make sure that the secret link for the record was created
        record = service.read(identity=owner_identity, id_=record.id)
        secret_links = record._obj.parent.access.links
        assert len(secret_links) == 1
        secret_link = secret_links[0].resolve()
        assert secret_link.token == args["token"]
        assert secret_link.permission_level == "view"
        assert secret_link.origin == f"request:{request.id}"


def test_manager_can_accept_user_access_request(
    running_app, client, users, minimal_record
):
    """A user with manage grant can accept a user access request,  but an editor cannot."""
    record_owner, user = users
    identity = _identity(record_owner)
    login_user(user)
    login_user_via_session(client, email=user.email)

    record = _create_public_record_restricted_files(identity, minimal_record)

    # Create a third user as the manager
    datastore = running_app.app.extensions["security"].datastore
    manager = datastore.create_user(
        email="manager@example.com", password="password1", active=True
    )
    db.session.commit()
    manager_identity = _identity(manager)
    _grant_permission(record.id, manager.id, "manage")

    # Create a final user as editor
    editor = datastore.create_user(
        email="editor@example.com", password="password2", active=True
    )
    db.session.commit()
    editor_identity = _identity(editor)
    _grant_permission(record.id, editor.id, "edit")

    # User submits the request
    response = client.post(
        f"/records/{record.id}/access/request",
        json={
            "message": "Please give me access!",
            "email": user.email,
            "full_name": "User",
        },
    )
    assert response.status_code == 200
    request_id = response.json["id"]

    # Editor cannot read the request
    with pytest.raises(PermissionDeniedError):
        current_requests_service.read(editor_identity, request_id)

    # Editor cannot accept the request
    with pytest.raises(PermissionDeniedError):
        current_requests_service.execute_action(
            editor_identity, request_id, "accept", data={}
        )

    # The manager accepts the request
    current_requests_service.execute_action(
        manager_identity, request_id, "accept", data={}
    )

    result = current_requests_service.read(system_identity, request_id)
    assert result["status"] == "accepted"

    # Verify the created access grant
    record = service.read(identity=identity, id_=record.id)
    grants = record._record.parent.access.grants
    assert len(grants) == 3  # Manager, editor and viewer
    assert grants[2].to_dict() == {
        "subject": {"type": "user", "id": str(user.id)},
        "permission": "view",
        "origin": f"request:{request_id}",
    }


def test_access_grant_for_role(
    running_app,
    client,
    users,
    roles,
    minimal_restricted_record,
):
    """Test whether we can grant access permissions to groups of users."""
    # Log in a user (wo we need to add to a group)
    user, role = users[-1], roles[-1]
    current_datastore.add_role_to_user(user, role)
    db.session.commit()
    login_user(user)
    login_user_via_session(client, email=user.email)

    # Create a restricted record
    draft = service.create(identity=system_identity, data=minimal_restricted_record)
    record = service.publish(identity=system_identity, id_=draft.id)

    response = client.get(f"/records/{record.id}")
    assert response.status_code == 403

    # Grant access to users with a specific role (i.e. in a specific group)
    service.access.bulk_create_grants(
        identity=system_identity,
        id_=record.id,
        data={
            "grants": [
                {
                    "subject": {
                        "type": "role",
                        "id": str(role.id),
                    },
                    "permission": "view",
                }
            ]
        },
    )

    response = client.get(f"/records/{record.id}")
    assert response.status_code == 200
