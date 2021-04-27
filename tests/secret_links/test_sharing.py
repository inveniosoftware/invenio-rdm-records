# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test sharing of restricted records via secret links."""

from io import BytesIO

import pytest
from flask_principal import AnonymousIdentity, Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user
from invenio_db import db
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow.exceptions import ValidationError

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.secret_links.permissions import LinkNeed


@pytest.fixture()
def identity(identity_simple):
    """Ensure it's an authenticated user."""
    identity_simple.provides.add(authenticated_user)
    return identity_simple


@pytest.fixture()
def service(app, client, location, es_clear):
    """RDM Record Service."""
    return app.extensions['invenio-rdm-records'].records_service


@pytest.fixture()
def restricted_record(service, minimal_record, identity):
    """Restricted record fixture."""
    data = minimal_record.copy()
    data["files"]["enabled"] = True
    data["access"]["record"] = "restricted"
    data["access"]["files"] = "restricted"

    # Create
    draft = service.create(identity, data)

    # Add a file
    service.draft_files.init_files(
        draft.id, identity, data=[{'key': 'test.pdf'}])
    service.draft_files.set_file_content(
        draft.id, 'test.pdf', identity, BytesIO(b'test file')
    )
    service.draft_files.commit_file(
        draft.id, 'test.pdf', identity)

    # Publish
    record = service.publish(draft.id, identity)

    # Put in edit mode so that draft exists
    draft = service.edit(draft.id, identity)

    return record


def test_invalid_level(service, restricted_record, identity):
    """Test invalid permission level."""
    record = restricted_record
    with pytest.raises(ValidationError):
        service.create_secret_link(record.id, identity, {
            "permission": "invalid"
        })


def test_permission_levels(service, restricted_record, identity, client):
    """Test invalid permission level."""
    id_ = restricted_record.id
    view_link = service.create_secret_link(
        id_, identity, {"permission": "view"})
    preview_link = service.create_secret_link(
        id_, identity, {"permission": "preview"})
    edit_link = service.create_secret_link(
        id_, identity, {"permission": "edit"})

    # == Anonymous user
    anon = AnonymousIdentity()
    anon.provides.add(any_user)

    # Deny anonymous to read restricted record and draft
    pytest.raises(PermissionDeniedError, service.read, id_, anon)
    pytest.raises(PermissionDeniedError, service.files.list_files, id_, anon)
    pytest.raises(PermissionDeniedError, service.read_draft, id_, anon)
    pytest.raises(
        PermissionDeniedError, service.draft_files.list_files, id_, anon)

    # === Anonymous user with view link ===
    anon.provides.add(LinkNeed(view_link.id))

    # Allow anonymous with view link to read record
    service.read(id_, anon)
    service.files.list_files(id_, anon)

    # Deny anonymous with view link to read draft
    pytest.raises(PermissionDeniedError, service.read_draft, id_, anon)
    pytest.raises(
        PermissionDeniedError, service.draft_files.list_files, id_, anon)

    # === Anonymous user with preview link ===
    anon.provides.remove(LinkNeed(view_link.id))
    anon.provides.add(LinkNeed(preview_link.id))

    # Allow anonymous with preview link to read record and draft
    service.read(id_, anon)
    service.files.list_files(id_, anon)
    service.read_draft(id_, anon)
    service.draft_files.list_files(id_, anon)
    service.draft_files.get_file_content(id_, 'test.pdf', anon)
    service.draft_files.read_file_metadata(id_, 'test.pdf', anon)

    # Deny anonymous with preview link to update/delete/edit/publish draft
    pytest.raises(PermissionDeniedError, service.update_draft, id_, anon, {})
    pytest.raises(PermissionDeniedError, service.edit, id_, anon)
    pytest.raises(PermissionDeniedError, service.delete_draft, id_, anon)
    pytest.raises(PermissionDeniedError, service.new_version, id_, anon)
    pytest.raises(PermissionDeniedError, service.publish, id_, anon)
    pytest.raises(
        PermissionDeniedError,
        service.draft_files.init_files, id_, anon, {})
    pytest.raises(
        PermissionDeniedError,
        service.draft_files.update_file_metadata, id_, 'test.pdf', anon, {})
    pytest.raises(
        PermissionDeniedError,
        service.draft_files.commit_file, id_, 'test.pdf', anon)
    pytest.raises(
        PermissionDeniedError,
        service.draft_files.delete_file, id_, 'test.pdf', anon)
    pytest.raises(
        PermissionDeniedError,
        service.draft_files.delete_all_files, id_, anon)
    pytest.raises(
        PermissionDeniedError,
        service.draft_files.set_file_content, id_, 'test.pdf', anon, None)

    # === Authenticated user with edit link ===
    i = Identity(100)
    i.provides.add(UserNeed(100))
    i.provides.add(authenticated_user)
    i.provides.add(LinkNeed(edit_link.id))

    # Allow user with edit link to read record and draft
    service.read(id_, i)
    service.files.list_files(id_, i)
    service.read_draft(id_, i)
    service.draft_files.list_files(id_, i)
    service.draft_files.get_file_content(id_, 'test.pdf', i)
    service.draft_files.read_file_metadata(id_, 'test.pdf', i)

    # Deny user with edit link to share the links
    pytest.raises(
        PermissionDeniedError, service.create_secret_link, id_, i, {})
    pytest.raises(
        PermissionDeniedError, service.read_secret_links, id_, i)
    pytest.raises(
        PermissionDeniedError, service.read_secret_link, id_, i, edit_link.id)
    pytest.raises(
        PermissionDeniedError,
        service.update_secret_link, id_, i, edit_link.id, {})
    pytest.raises(
        PermissionDeniedError,
        service.delete_secret_link, id_, i, edit_link.id)

    # Allow user with edit link to update, delete, edit, publish
    draft = service.read_draft(id_, i)
    data = draft.data
    data['metadata']['title'] = 'allow it'
    service.update_draft(id_, i, data)
    service.delete_draft(id_, i)
    service.edit(id_, i)
    service.publish(id_, i)
    new_draft = service.new_version(id_, i)
    new_id = new_draft.id
    service.import_files(new_id, i)
    service.draft_files.delete_file(new_id, 'test.pdf', i)


def test_read_restricted_record_with_secret_link(
    app, client, location, minimal_record, es_clear, identity_simple
):
    """Test access to a restricted record via a shared link."""
    identity_simple.provides.add(authenticated_user)
    service = current_rdm_records.records_service
    record_data = minimal_record.copy()
    record_data["access"]["files"] = "restricted"
    record_data["access"]["record"] = "restricted"

    draft = service.create(identity=identity_simple, data=record_data)
    record = service.publish(id_=draft.id, identity=identity_simple)
    recid = record.id

    link = record._record.parent.access.links.create(
        permission_level="view",
    )

    # FIXME without this, commit() won't work (b/c of jsonschema)
    record._record.pop("status", None)
    record._record.commit()
    record._record.parent.commit()
    db.session.commit()

    # the record shouldn't be accessible without login and/or token
    response = client.get(f"/records/{recid}")
    assert response.status_code == 403

    # but it should be accessible with the token
    response = client.get(
        f"/records/{recid}",
        query_string={"token": link.token},
    )
    assert response.status_code == 200

    # the record shouldn't be showing up in search results, however
    RDMRecord.index.refresh()
    res = client.get(
        "/records", query_string={"q": f"id:{recid}"}
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0
