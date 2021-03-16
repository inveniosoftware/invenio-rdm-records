# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test sharing of restricted records via secret links."""

from invenio_access.permissions import authenticated_user
from invenio_db import db

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord


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
        permission_level="read",
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
