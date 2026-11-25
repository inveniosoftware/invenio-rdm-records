# SPDX-FileCopyrightText: 2026 Max Hawkins.
# SPDX-License-Identifier: MIT

"""Tests that the record owner is only exposed to users allowed to see it."""

import pytest
from flask_principal import AnonymousIdentity
from invenio_access.permissions import any_user, system_identity

from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_rdm_records.records import RDMRecord


@pytest.fixture()
def anon_identity():
    """Anonymous (not logged in) identity."""
    identity = AnonymousIdentity()
    identity.provides.add(any_user)
    return identity


@pytest.fixture()
def owned_record(record_factory, uploader):
    """Public record owned by ``uploader`` and not part of any community."""
    return record_factory.create_record(uploader=uploader, community=None)


def _owner(data):
    return data["parent"]["access"].get("owned_by")


def _expanded_owner(data):
    return data.get("expanded", {}).get("parent", {}).get("access", {}).get("owned_by")


def test_owner_hidden_on_read(running_app, owned_record, anon_identity, test_user):
    """Anonymous and unrelated users don't get the owner, expanded or not."""
    for identity in [anon_identity, test_user.identity]:
        data = service.read(identity, owned_record["id"], expand=True).to_dict()

        assert _owner(data) is None
        assert _expanded_owner(data) is None
        # other parent access fields are unaffected
        assert "settings" in data["parent"]["access"]


def test_owner_hidden_in_search(running_app, owned_record, anon_identity):
    """Search results don't leak the owner either."""
    RDMRecord.index.refresh()

    hits = list(service.search(anon_identity, expand=True).hits)

    assert hits
    for hit in hits:
        assert _owner(hit) is None
        assert _expanded_owner(hit) is None


def test_owner_visible_to_privileged_users(running_app, owned_record, uploader):
    """Owner, superusers and system processes still see the owner."""
    identities = [
        uploader.identity,
        running_app.superuser_identity,
        system_identity,
    ]
    for identity in identities:
        data = service.read(identity, owned_record["id"], expand=True).to_dict()

        assert _owner(data) == {"user": str(uploader.id)}
        assert str(_expanded_owner(data)["id"]) == str(uploader.id)
