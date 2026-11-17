# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2023 Northwestern University.
# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""External provider tests."""

import pytest
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services.pids.providers import (
    BlockedPrefixes,
    ExternalPIDProvider,
)


@pytest.fixture(scope="function")
def external_provider():
    """Application factory fixture."""
    return ExternalPIDProvider("external", "testid", label="DOI")


@pytest.fixture(scope="function")
def record(location, db):
    """Creates an empty record."""
    draft = RDMDraft.create({})
    record = RDMRecord.publish(draft)
    return record


def test_external_provider_create(record, external_provider, db):
    created_pid = external_provider.create(record, "avalue")
    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="testid"
    )

    assert created_pid == db_pid
    assert created_pid.pid_value
    assert created_pid.pid_type == "testid"
    assert created_pid.status == PIDStatus.NEW


def test_external_provider_get(record, external_provider, db):
    created_pid = external_provider.create(record, "avalue")
    get_pid = external_provider.get(created_pid.pid_value)

    assert created_pid == get_pid
    assert get_pid.pid_value
    assert get_pid.pid_type == "testid"
    assert get_pid.status == PIDStatus.NEW


def test_external_provider_register(record, external_provider, db):
    created_pid = external_provider.create(record, "avalue")
    assert external_provider.register(pid=created_pid, record=record)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="testid"
    )

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "testid"
    assert db_pid.status == PIDStatus.REGISTERED


def test_external_provider_validate(running_app, db, external_provider, record):
    success, errors = external_provider.validate(
        record=record, identifier="somevalue", provider="external"
    )
    assert success
    assert not errors


def test_external_provider_validate_failure(running_app, db, external_provider, record):
    # Case - client not supported for provider
    with pytest.raises(Exception):
        external_provider.validate(
            record=record, client="someclient", provider="external"
        )

    # Case - provider name invalid
    with pytest.raises(Exception):
        external_provider.validate(record=record, provider="wrong")

    # Case - missing identifier
    success, errors = external_provider.validate(record=record, provider="external")
    assert not success
    assert "Missing DOI for required field." in errors[0]["messages"]


def test_blocked_prefixes_ignores_empty_prefix(running_app):
    """Ensure empty configured prefixes do not block all external DOIs."""
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "THEME_SITENAME": "TestSite",
            "DATACITE_PREFIX": "",
            "CROSSREF_PREFIX": "",
        }
    )

    try:
        validator = BlockedPrefixes(config_names=["DATACITE_PREFIX", "CROSSREF_PREFIX"])
        errors = []

        validator(
            record=None,
            identifier="10.1234/external",
            provider="external",
            errors=errors,
        )

        assert errors == []
    finally:
        current_app.config.clear()
        current_app.config.update(old_config)


def _duplicate_setup(provider, location, db):
    """Publish a record holding an external PID and return it with a new draft."""
    first = RDMRecord.publish(RDMDraft.create({}))
    first.commit()
    pid = provider.create(first, "dup-value")
    provider.register(pid=pid, record=first)
    db.session.commit()
    other = RDMRecord.publish(RDMDraft.create({}))
    return first, other


def test_external_provider_duplicate_default_message(
    running_app, location, db, external_provider
):
    """By default the duplicate error does not reveal the existing record."""
    _, other = _duplicate_setup(external_provider, location, db)
    success, errors = external_provider.validate(
        record=other, identifier="dup-value", provider="external"
    )
    assert not success
    messages = [str(m) for m in errors[0]["messages"]]
    assert messages == ["testid:dup-value already exists."]


def test_external_provider_duplicate_links_existing_record(
    running_app, location, db, monkeypatch
):
    """With the option enabled the error links the readable existing record."""
    provider = ExternalPIDProvider(
        "external", "testid", label="DOI", link_existing_record=True
    )
    _, other = _duplicate_setup(provider, location, db)
    url = "https://example.org/records/abcde-12345"
    monkeypatch.setattr(provider, "_existing_record_url", lambda pid: url)
    success, errors = provider.validate(
        record=other, identifier="dup-value", provider="external"
    )
    assert not success
    assert [str(m) for m in errors[0]["messages"]] == [
        f"DOI dup-value is already used by the record {url}"
    ]


def test_external_provider_duplicate_unreadable_record(
    running_app, location, db, monkeypatch
):
    """If no URL can be given (draft/unreadable) the generic message is kept."""
    provider = ExternalPIDProvider(
        "external", "testid", label="DOI", link_existing_record=True
    )
    _, other = _duplicate_setup(provider, location, db)
    monkeypatch.setattr(provider, "_existing_record_url", lambda pid: None)
    success, errors = provider.validate(
        record=other, identifier="dup-value", provider="external"
    )
    assert not success
    messages = [str(m) for m in errors[0]["messages"]]
    assert messages == ["testid:dup-value already exists."]
