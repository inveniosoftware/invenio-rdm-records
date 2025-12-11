# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Testing the workflow for access requests."""

import copy
import io
import re
import urllib

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
from invenio_requests.proxies import current_requests_service

from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_rdm_records.requests.access import AccessRequestTokenNeed


def test_simple_guest_access_request_flow(running_app, client, users, minimal_record):
    """Test a the simple guest-based access request flow."""
    with running_app.app.extensions["mail"].record_messages() as outbox:
        # Log in a user (whose ID we need later)
        record_owner, _ = users
        identity = Identity(record_owner.id)
        identity.provides.add(any_user)
        identity.provides.add(authenticated_user)
        identity.provides.add(UserNeed(record_owner.id))
        guest_identity = Identity(None)
        guest_identity.provides.add(any_user)

        # Create a public record with some restricted files
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
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(request.id) in guest_submit_message.html
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
    """Test a the simple user-based access request flow."""

    with running_app.app.extensions["mail"].record_messages() as outbox:
        # Log in a user (whose ID we need later)
        record_owner, user = users
        identity = Identity(record_owner.id)
        identity.provides.add(any_user)
        identity.provides.add(authenticated_user)
        identity.provides.add(UserNeed(record_owner.id))
        login_user(user)
        login_user_via_session(client, email=user.email)

        # Create a public record with some restricted files
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
        # this tests pre-existing functionality although /me/requests/{} could
        # work as well semantically
        assert f"/access/requests/{request_id}" in response.json["links"]["self_html"]
        assert len(outbox) == 1
        submit_message = outbox[0]
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(request_id) in submit_message.html

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
                        "id": str(role.name),
                    },
                    "permission": "view",
                }
            ]
        },
    )

    response = client.get(f"/records/{record.id}")
    assert response.status_code == 200
