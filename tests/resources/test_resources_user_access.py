# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for RDMGrantsAccessResource."""

import json

from tests.helpers import login_user, logout_user


def test_read_by_subject_found(
    running_app, client, minimal_record, headers, community_owner, users
):
    """Test read grant by user id."""
    # create record
    login_user(client, users[0])
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]
    user_id = community_owner.id

    # create grant
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    response = client.post(
        f"/records/{recid}/access/grants", json=grant_payload, headers=headers
    )
    assert response.status_code == 201

    # read grant
    response = client.get(f"/records/{recid}/access/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json["permission"] == "preview"
    assert response.json["subject"]["id"] == user_id
    assert response.json["subject"]["type"] == "user"

    # read as an anonymous user
    logout_user(client)
    response = client.get(f"/records/{recid}/access/users/{user_id}", headers=headers)
    assert response.status_code == 403

    # read as a different user
    login_user(client, users[1])
    response = client.get(f"/records/{recid}/access/users/{user_id}", headers=headers)
    assert response.status_code == 403


def test_read_by_subject_not_found(
    running_app, client_with_login, minimal_record, headers, community_owner
):
    """Test read grant by user id. Not found."""
    # create record
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]
    user_id = community_owner.id

    # create grant
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    response = client.post(
        f"/records/{recid}/access/grants", json=grant_payload, headers=headers
    )
    assert response.status_code == 201

    # read grant with different user id
    response = client.get(f"/records/{recid}/access/users/3", headers=headers)
    assert response.status_code == 404
    assert response.json["message"] == "No grant found by given user id."


def test_delete_by_subject_found(
    running_app, client, users, minimal_record, headers, community_owner
):
    """Test delete grant by user id."""
    # create record
    login_user(client, users[0])
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]
    user_id = community_owner.id

    # create grant
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
            }
        ]
    }
    response = client.post(
        f"/records/{recid}/access/grants", json=grant_payload, headers=headers
    )
    assert response.status_code == 201

    # read grant
    response = client.get(f"/records/{recid}/access/users/{user_id}", headers=headers)
    assert response.status_code == 200

    # try to delete as an anonymous user
    logout_user(client)
    response = client.delete(
        f"/records/{recid}/access/users/{user_id}", headers=headers
    )
    assert response.status_code == 403

    # try to delete as a different user
    login_user(client, users[1])
    response = client.delete(
        f"/records/{recid}/access/users/{user_id}", headers=headers
    )
    assert response.status_code == 403
    logout_user(client)

    # delete grant
    login_user(client, users[0])
    response = client.delete(
        f"/records/{recid}/access/users/{user_id}", headers=headers
    )
    assert response.status_code == 204

    # read grant
    response = client.get(f"/records/{recid}/access/users/{user_id}", headers=headers)
    assert response.status_code == 404
    assert response.json["message"] == "No grant found by given user id."


def test_delete_by_subject_id_not_found(
    running_app, client_with_login, minimal_record, headers
):
    """Test delete grant by user id. Not found."""
    # create record
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]

    # delete grant
    response = client.delete(f"/records/{recid}/access/users/2", headers=headers)
    assert response.status_code == 404
    assert response.json["message"] == "No grant found by given user id."


def test_search_grants_by_subject(
    running_app, client, users, minimal_record, headers, community_owner, curator
):
    """Test get all user grants for record."""
    # create record
    login_user(client, users[0])
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]

    user_id = community_owner.id
    user_id2 = curator.id

    # create user grants
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "edit",
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
    response = client.post(
        f"/records/{recid}/access/grants", json=grant_payload2, headers=headers
    )
    assert response.status_code == 201

    response = client.post(
        f"/records/{recid}/access/grants", json=grant_payload, headers=headers
    )
    assert response.status_code == 201

    # search user grants
    response = client.get(f"/records/{recid}/access/users", headers=headers)
    assert response.status_code == 200
    assert response.json["hits"]["total"] == 2
    assert response.json["hits"]["hits"][0]["subject"]["type"] == "user"
    assert response.json["hits"]["hits"][0]["subject"]["id"] == user_id2
    assert response.json["hits"]["hits"][1]["subject"]["type"] == "user"
    assert response.json["hits"]["hits"][1]["subject"]["id"] == user_id

    # search as an anonymous user
    logout_user(client)
    response = client.get(f"/records/{recid}/access/users", headers=headers)
    assert response.status_code == 403

    # search as a different user
    login_user(client, users[1])
    response = client.get(f"/records/{recid}/access/users", headers=headers)
    assert response.status_code == 403


def test_search_grants_by_subject_not_found(
    running_app, client_with_login, minimal_record, headers
):
    """Test get all user grants for record. Not found."""
    # create record
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]

    # search user grants
    response = client.get(f"/records/{recid}/access/users", headers=headers)
    assert response.status_code == 200
    assert response.json["hits"]["total"] == 0


def test_patch_grants_by_subject(
    running_app, client, users, minimal_record, headers, community_owner
):
    """Test partial update of user grants for record."""
    # create record
    login_user(client, users[0])
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]
    user_id = community_owner.id

    # create user grants
    grant_payload = {
        "grants": [
            {
                "subject": {"type": "user", "id": user_id},
                "permission": "preview",
                "origin": "origin",
            }
        ]
    }
    response = client.post(
        f"/records/{recid}/access/grants", json=grant_payload, headers=headers
    )
    assert response.status_code == 201

    payload = {
        "permission": "manage",
    }

    # update as an anonymous user
    logout_user(client)
    response = client.patch(
        f"/records/{recid}/access/users/{user_id}", json=payload, headers=headers
    )
    assert response.status_code == 403

    # update as a different user
    login_user(client, users[1])
    response = client.patch(
        f"/records/{recid}/access/users/{user_id}", json=payload, headers=headers
    )
    assert response.status_code == 403
    logout_user(client)

    # update grant
    login_user(client, users[0])
    response = client.patch(
        f"/records/{recid}/access/users/{user_id}", json=payload, headers=headers
    )
    assert response.status_code == 200

    # read grant
    response = client.get(f"/records/{recid}/access/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json["permission"] == "manage"


def test_patch_grants_by_subject_not_found(
    running_app, client_with_login, minimal_record, headers
):
    """Test partial update of user grants for record. Not found"""
    # create record
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]

    # update grant
    payload = {
        "permission": "manage",
    }
    response = client.patch(
        f"/records/{recid}/access/users/55", json=payload, headers=headers
    )
    assert response.status_code == 404
    assert response.json["message"] == "No grant found by given user id."
