# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Test naming the existing record in duplicate external PID errors."""

from copy import deepcopy

import pytest
from flask import g
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import ValidationErrorWithMessageAsList
from invenio_rdm_records.services.pids import providers

DOI = "10.9999/external.1"


def _external_provider(link_existing_record):
    return providers.ExternalPIDProvider(
        "external",
        "doi",
        validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
        label=_("DOI"),
        link_existing_record=link_existing_record,
    )


@pytest.fixture(scope="module", params=[False, True], ids=["off", "on"])
def link_existing_record(request):
    """Whether the external provider links the existing record."""
    return request.param


@pytest.fixture(scope="module")
def app_config(app_config, link_existing_record):
    """Replace the external provider with one using the option under test."""
    app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        _external_provider(link_existing_record) if p.name == "external" else p
        for p in app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"]
    ]
    return app_config


@pytest.fixture()
def service(running_app):
    """Records service."""
    return current_rdm_records.records_service


def _external_doi_data(record, doi=DOI):
    data = deepcopy(record)
    data["pids"] = {"doi": {"identifier": doi, "provider": "external"}}
    return data


def _publish_duplicate(service, identity, data):
    """Publish a second record with the same DOI; return the error messages."""
    draft = service.create(identity, data)
    with pytest.raises(ValidationErrorWithMessageAsList) as exc:
        service.publish(identity, draft.id)
    return _flatten(exc.value.messages)


def _flatten(errors):
    """Return the error messages as plain strings."""
    return [str(m) for error in errors for m in error["messages"]]


def _generic_message(messages):
    return any("already exists" in m for m in messages)


def test_published_record_is_named(
    running_app,
    search_clear,
    service,
    minimal_record,
    superuser_identity,
    link_existing_record,
):
    """A readable published record is named only when the option is on."""
    data = _external_doi_data(minimal_record)
    first = service.publish(
        superuser_identity, service.create(superuser_identity, data).id
    )
    g.identity = superuser_identity

    messages = _publish_duplicate(service, superuser_identity, data)

    if link_existing_record:
        url = first.links["self_html"]
        assert messages == [f"DOI {DOI} is already used by the record {url}."]
    else:
        assert _generic_message(messages)
        assert not any("/records/" in m for m in messages)


def test_unreadable_record_is_not_named(
    running_app,
    search_clear,
    service,
    minimal_restricted_record,
    superuser_identity,
    anonymous_identity,
):
    """A restricted record the current identity can't read is never named."""
    data = _external_doi_data(minimal_restricted_record)
    first = service.publish(
        superuser_identity, service.create(superuser_identity, data).id
    )
    # the request identity cannot read the restricted record
    g.identity = anonymous_identity

    messages = _publish_duplicate(service, superuser_identity, data)

    assert _generic_message(messages)
    assert first.id not in " ".join(messages)


def test_draft_is_not_named(
    running_app,
    search_clear,
    service,
    minimal_record,
    superuser_identity,
):
    """A DOI held only by a draft keeps the generic message."""
    draft = service.create(superuser_identity, deepcopy(minimal_record))
    # external PIDs are only stored at publish time, so reserve it by hand
    draft_uuid = service.draft_cls.pid.resolve(draft.id, registered_only=False).id
    PersistentIdentifier.create(
        "doi",
        DOI,
        object_type="rec",
        object_uuid=draft_uuid,
        status=PIDStatus.RESERVED,
    )
    g.identity = superuser_identity

    other = service.create(superuser_identity, _external_doi_data(minimal_record))
    with pytest.raises(ValidationErrorWithMessageAsList) as exc:
        service.publish(superuser_identity, other.id)

    messages = _flatten(exc.value.messages)
    assert _generic_message(messages)
    assert draft.id not in " ".join(messages)
