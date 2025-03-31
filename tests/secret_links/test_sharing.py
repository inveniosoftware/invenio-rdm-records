# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test sharing of restricted records via secret links."""

from io import BytesIO

import pytest
from flask_principal import AnonymousIdentity, Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user
from invenio_db import db
from invenio_records_resources.services.errors import (
    PermissionDeniedError,
    RecordPermissionDeniedError,
)
from marshmallow.exceptions import ValidationError

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.secret_links.permissions import LinkNeed


@pytest.fixture()
def service(running_app, search_clear):
    """RDM Record Service."""
    return running_app.app.extensions["invenio-rdm-records"].records_service


@pytest.fixture()
def restricted_record(service, minimal_record, identity_simple):
    """Restricted record fixture."""
    data = minimal_record.copy()
    data["files"]["enabled"] = True
    data["access"]["record"] = "restricted"
    data["access"]["files"] = "restricted"

    # Create
    draft = service.create(identity_simple, data)

    # Add a file
    service.draft_files.init_files(
        identity_simple, draft.id, data=[{"key": "test.pdf"}]
    )
    service.draft_files.set_file_content(
        identity_simple, draft.id, "test.pdf", BytesIO(b"test file")
    )
    service.draft_files.commit_file(identity_simple, draft.id, "test.pdf")

    # Publish
    record = service.publish(identity_simple, draft.id)

    # Put in edit mode so that draft exists
    draft = service.edit(identity_simple, draft.id)

    return record


def test_invalid_level(service, restricted_record, identity_simple):
    """Test invalid permission level."""
    record = restricted_record
    with pytest.raises(ValidationError):
        service.access.create_secret_link(
            identity_simple, record.id, {"permission": "invalid"}
        )


def test_permission_levels(service, restricted_record, identity_simple, client):
    """Test invalid permission level."""
    id_ = restricted_record.id
    view_link = service.access.create_secret_link(
        identity_simple, id_, {"permission": "view"}
    )
    preview_link = service.access.create_secret_link(
        identity_simple, id_, {"permission": "preview"}
    )
    edit_link = service.access.create_secret_link(
        identity_simple, id_, {"permission": "edit"}
    )

    # == Anonymous user
    anon = AnonymousIdentity()
    anon.provides.add(any_user)

    # Deny anonymous to read restricted record and draft
    pytest.raises(RecordPermissionDeniedError, service.read, anon, id_)
    pytest.raises(PermissionDeniedError, service.files.list_files, anon, id_)
    pytest.raises(PermissionDeniedError, service.read_draft, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.list_files(anon, id_)

    # === Anonymous user with view link ===
    anon.provides.add(LinkNeed(view_link.id))

    # Allow anonymous with view link to read record
    service.read(anon, id_)
    service.files.list_files(anon, id_)

    # Deny anonymous with view link to read draft
    pytest.raises(PermissionDeniedError, service.read_draft, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.list_files(anon, id_)

    # === Anonymous user with preview link ===
    anon.provides.remove(LinkNeed(view_link.id))
    anon.provides.add(LinkNeed(preview_link.id))

    # Allow anonymous with preview link to read record and draft
    service.read(anon, id_)
    service.files.list_files(anon, id_)
    service.read_draft(anon, id_)
    service.draft_files.list_files(anon, id_)
    service.draft_files.get_file_content(anon, id_, "test.pdf")
    service.draft_files.read_file_metadata(anon, id_, "test.pdf")

    # Deny anonymous with preview link to update/delete/edit/publish draft
    pytest.raises(PermissionDeniedError, service.update_draft, anon, id_, {})
    pytest.raises(PermissionDeniedError, service.edit, anon, id_)
    pytest.raises(PermissionDeniedError, service.delete_draft, anon, id_)
    pytest.raises(PermissionDeniedError, service.new_version, anon, id_)
    pytest.raises(PermissionDeniedError, service.publish, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(anon, id_, [{"key": "test.pdf"}])
    with pytest.raises(PermissionDeniedError):
        service.draft_files.update_file_metadata(anon, id_, "test.pdf", {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.commit_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_all_files(anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.set_file_content(anon, id_, "test.pdf", None)

    # === Authenticated user with edit link ===
    i = Identity(100)
    i.provides.add(UserNeed(100))
    i.provides.add(authenticated_user)
    i.provides.add(LinkNeed(edit_link.id))

    # Allow user with edit link to read record and draft
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny user with edit link to share the links
    with pytest.raises(PermissionDeniedError):
        service.access.create_secret_link(i, id_, {})
    with pytest.raises(PermissionDeniedError):
        service.access.read_all_secret_links(i, id_)
    with pytest.raises(PermissionDeniedError):
        service.access.read_secret_link(i, id_, edit_link.id)
    with pytest.raises(PermissionDeniedError):
        service.access.update_secret_link(i, id_, edit_link.id, {})
    with pytest.raises(PermissionDeniedError):
        service.access.delete_secret_link(i, id_, edit_link.id)

    # Allow user with edit link to update, delete, edit, publish
    draft = service.read_draft(i, id_)
    data = draft.data
    data["metadata"]["title"] = "allow it"
    service.update_draft(i, id_, data)
    service.delete_draft(i, id_)
    test = service.edit(i, id_)
    service.publish(i, id_)
    new_draft = service.new_version(i, id_)
    new_id = new_draft.id
    service.import_files(i, new_id)
    service.draft_files.delete_file(i, new_id, "test.pdf")


def test_read_restricted_record_with_secret_link(
    service, minimal_record, identity_simple, client
):
    """Test access to a restricted record via a shared link."""
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
    res = client.get("/records", query_string={"q": f"id:{recid}"})
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0
