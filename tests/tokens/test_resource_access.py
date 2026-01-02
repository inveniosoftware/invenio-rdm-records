# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Resource access tokens."""

from datetime import datetime, timedelta
from io import BytesIO

import jwt
import pytest
from invenio_oauth2server.models import Token

from invenio_rdm_records.tokens import validate_rat
from invenio_rdm_records.tokens.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenIDError,
    MissingTokenIDError,
    TokenDecodeError,
)
from invenio_rdm_records.tokens.scopes import tokens_generate_scope


def _generate_pat_token(
    db,
    uploader,
    client,
    access_token,
    scope=tokens_generate_scope.id,
    expires=datetime.utcnow() + timedelta(hours=10),
):
    """Create a personal access token."""
    with db.session.begin_nested():
        token_ = Token(
            client_id=client,
            user_id=uploader.id,
            access_token=access_token,
            expires=expires,
            is_personal=False,
            is_internal=True,
        )
        db.session.add(token_)
    db.session.commit()

    token_.scopes = [scope]
    return dict(
        token=token_,
        auth_header=[
            ("Authorization", "Bearer {0}".format(token_.access_token)),
        ],
    )


def _rat_gen(token, payload=None, headers=None):
    """Create a resource access token."""
    payload = {"iat": datetime.utcnow()} if payload is None else payload
    headers = {"kid": str(token.id)} if headers is None else headers
    return jwt.encode(
        payload=payload,
        key=token.access_token,
        algorithm="HS256",
        headers=headers,
    )


def create_record_w_file(client, record, headers, is_published=True):
    """Create record with a file."""
    # Create draft
    record["files"] = {"enabled": True}
    response = client.post("/records", json=record, headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]

    # Attach a file to it
    response = client.post(
        f"/records/{recid}/draft/files", headers=headers, json=[{"key": "test.pdf"}]
    )
    assert response.status_code == 201
    response = client.put(
        f"/records/{recid}/draft/files/test.pdf/content",
        headers={
            "content-type": "application/octet-stream",
            "accept": "application/json",
        },
        data=BytesIO(b"testfile"),
    )
    assert response.status_code == 200
    response = client.post(
        f"/records/{recid}/draft/files/test.pdf/commit", headers=headers
    )
    assert response.status_code == 200

    # Publish it
    if is_published:
        response = client.post(
            f"/records/{recid}/draft/actions/publish", headers=headers
        )
        assert response.status_code == 202

    return recid


def test_rat_validation_failed(app, db, uploader, superuser_identity, oauth2_client):
    """Test possible validation failings of Resource access tokens."""
    # case: no headers in the token
    with pytest.raises(TokenDecodeError):
        validate_rat("not_a.valid_jwt")

    # case: headers don't have "kid"
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token1")
    with pytest.raises(MissingTokenIDError):
        validate_rat(_rat_gen(pat["token"], headers={}))

    # case: "kid" is not a digit
    with pytest.raises(InvalidTokenIDError):
        validate_rat(_rat_gen(pat["token"], headers={"kid": "invalid"}))

    # case: PAT with given id doesn't exist
    with pytest.raises(InvalidTokenError):
        validate_rat(_rat_gen(pat["token"], headers={"kid": "99999"}))

    # case: PAT is in the wrong scope
    pat = _generate_pat_token(
        db, uploader, oauth2_client, "rat_token2", scope="user:email"
    )
    with pytest.raises(InvalidTokenError):
        validate_rat(_rat_gen(pat["token"]))

    # case: RAT is expired
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token3")
    with pytest.raises(ExpiredTokenError):
        # generate token issued an hour ago
        validate_rat(
            _rat_gen(
                pat["token"],
                payload={"iat": datetime.utcnow() - timedelta(hours=1), "sub": {}},
            )
        )
    # case: RAT is missing "sub" key
    with pytest.raises(InvalidTokenError):
        validate_rat(_rat_gen(pat["token"]))
    # case: RAT has a non-dictionary "sub" key
    with pytest.raises(InvalidTokenError):
        validate_rat(_rat_gen(pat["token"], payload={"sub": "test-string-sub"}))


def test_rec_files_permissions_with_rat(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test access to restricted files of a record with valid RAT for rec owner, other user and unknown user."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    test_user.logout(client)

    # anonymous user with token can access the files
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200


def test_rec_metadata_permissions_with_rat(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test access to metadata of a record with restricted files using valid RAT."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf"

    # record owner with token can access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    test_user.logout(client)

    # anonymous user with token can access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 200


def test_draft_files_permissions_with_rat(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test access to restricted files of a draft with valid RAT for rec owner, other user and unknown user."""
    # create draft
    draft_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(
        draft_owner, minimal_record, headers, is_published=False
    )

    # generate RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    draft_file_url = f"/records/{recid}/draft/files/test.pdf/content"

    # draft owner with token can access the files
    res = draft_owner.get(
        draft_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can access the files
    other_user = test_user.login(client)
    res = other_user.get(
        draft_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    test_user.logout(client)

    # anonymous user with token can access the files
    res = client.get(draft_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 200


def test_draft_metadata_permissions_with_rat(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test access to metadata of a draft with restricted files using valid RAT."""
    # create draft
    draft_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(
        draft_owner, minimal_record, headers, is_published=False
    )

    # generate RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    draft_file_url = f"/records/{recid}/draft/files/test.pdf"

    # draft owner with token can access the files
    res = draft_owner.get(
        draft_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can access the files
    other_user = test_user.login(client)
    res = other_user.get(
        draft_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    test_user.logout(client)

    # anonymous user with token can access the files
    res = client.get(draft_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 200


def test_fully_restricted_rec_files_permissions_with_rat(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test access to files of a fully restricted record with valid RAT for rec owner, other user and unknown user."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["record"] = "restricted"
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    test_user.logout(client)

    # anonymous user with token can access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 200


def test_fully_restricted_draft_files_permissions_with_rat(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test access to files of a fully restricted draft with valid RAT for rec owner, other user and unknown user."""
    # create draft
    draft_owner = uploader.login(client)
    minimal_record["access"]["record"] = "restricted"
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(
        draft_owner, minimal_record, headers, is_published=False
    )

    # generate RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    draft_file_url = f"/records/{recid}/draft/files/test.pdf/content"

    # draft owner with token can access the files
    res = draft_owner.get(
        draft_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can access the files
    other_user = test_user.login(client)
    res = other_user.get(
        draft_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    test_user.logout(client)

    # anonymous user with token can access the files
    res = client.get(draft_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 200


def test_rec_files_permissions_with_rat_invalid_token_error(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test InvalidTokenError on access to restricted files of a record with invalid RAT."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with invalid scope
    pat = _generate_pat_token(
        db, uploader, oauth2_client, "rat_token", scope="user:email"
    )["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can NOT access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert res.json["message"] == "The resource access token is invalid."
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert res.json["message"] == "The resource access token is invalid."
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 400
    assert res.json["message"] == "The resource access token is invalid."


def test_rec_files_permissions_with_rat_missing_token_id_error(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test MissingTokenIDError on access to restricted files of a record with invalid RAT."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with empty headers
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can NOT access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert (
        res.json["message"]
        == 'Missing "kid" key with personal access token ID in JWT header of resource access token.'
    )
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert (
        res.json["message"]
        == 'Missing "kid" key with personal access token ID in JWT header of resource access token.'
    )
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 400
    assert (
        res.json["message"]
        == 'Missing "kid" key with personal access token ID in JWT header of resource access token.'
    )


def test_rec_files_permissions_with_rat_invalid_token_id_error(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test InvalidTokenIDError on access to restricted files of a record with invalid RAT."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with invalid headers
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": "invalid"},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can NOT access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert (
        res.json["message"]
        == '"kid" JWT header value of resource access token not a valid personal access token ID.'
    )
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert (
        res.json["message"]
        == '"kid" JWT header value of resource access token not a valid personal access token ID.'
    )
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 400
    assert (
        res.json["message"]
        == '"kid" JWT header value of resource access token not a valid personal access token ID.'
    )


def test_rec_files_permissions_with_rat_expired_token_error(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test ExpiredTokenError on access to restricted files of a record with invalid RAT."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate expired RAT
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={"iat": datetime.utcnow() - timedelta(hours=1), "sub": {}},
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can NOT access the files
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert res.json["message"] == "The resource access token is expired."
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 400
    assert res.json["message"] == "The resource access token is expired."
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 400
    assert res.json["message"] == "The resource access token is expired."


def test_rec_files_permissions_with_rat_wrong_file(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test PermissionDenied on access to restricted files of a record with wrong filename."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with different file names
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "another file.pdf",
                "access": "read",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can access the files (works permission of a RecordOwner())
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."


def test_rec_files_permissions_with_rat_wrong_access(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test PermissionDenied on access to restricted files of a record with wrong access level."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with different access level
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "another",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can access the files (works permission of a RecordOwner())
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."


def test_rec_files_permissions_with_rat_wrong_recid(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    test_user,
    oauth2_client,
):
    """Test PermissionDenied on access to restricted files of a record with wrong record id."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)
    another_recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with different record id
    pat = _generate_pat_token(db, uploader, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "another",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{another_recid}/files/test.pdf/content"

    # record owner with token can access the files (works permission of a RecordOwner())
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."


def test_rec_files_permissions_with_rat_wrong_signer(
    running_app,
    db,
    users,
    superuser_identity,
    minimal_record,
    client,
    headers,
    uploader,
    community_owner,
    test_user,
    oauth2_client,
):
    """Test PermissionDenied on access to restricted files of a record with wrong signer."""
    # create record
    record_owner = uploader.login(client)
    minimal_record["access"]["files"] = "restricted"
    recid = create_record_w_file(record_owner, minimal_record, headers)

    # generate RAT with PAT of a different user
    pat = _generate_pat_token(db, community_owner, oauth2_client, "rat_token")["token"]
    rat_token = jwt.encode(
        payload={
            "iat": datetime.utcnow(),
            "sub": {
                "record_id": recid,
                "file": "test.pdf",
                "access": "another",
            },
        },
        key=pat.access_token,
        algorithm="HS256",
        headers={"kid": str(pat.id)},
    )

    record_file_url = f"/records/{recid}/files/test.pdf/content"

    # record owner with token can access the files (works permission of a RecordOwner())
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 200
    uploader.logout(client)

    # other user with token can NOT access the files
    other_user = test_user.login(client)
    res = other_user.get(
        record_file_url, query_string={"resource_access_token": rat_token}
    )
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."
    test_user.logout(client)

    # anonymous user with token can NOT access the files
    res = client.get(record_file_url, query_string={"resource_access_token": rat_token})
    assert res.status_code == 403
    assert res.json["message"] == "Permission denied."
