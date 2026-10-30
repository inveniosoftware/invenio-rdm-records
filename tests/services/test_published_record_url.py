# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Test the link of a published record, looked up by its UUID."""

from uuid import uuid4

from invenio_rdm_records.proxies import current_rdm_records


def test_published_record_url(running_app, search_clear, minimal_record):
    """A published record is found by UUID; a draft or unknown UUID is not."""
    identity = running_app.superuser_identity
    service = current_rdm_records.records_service

    draft = service.create(identity, minimal_record)
    assert service.published_record_url(identity, draft._record.id) is None

    record = service.publish(identity, draft.id)
    url = service.published_record_url(identity, record._record.id)
    assert url == record.links["self_html"]

    assert service.published_record_url(identity, uuid4()) is None
