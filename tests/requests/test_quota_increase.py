# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Test quota increase requests."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.services.request_policies import QuotaIncreasePolicy


@pytest.fixture(scope="module")
def app_config(app_config):
    """Enable self-service quota increases."""
    app_config["RDM_IMMEDIATE_QUOTA_INCREASE_ENABLED"] = True
    app_config["RDM_IMMEDIATE_QUOTA_INCREASE_POLICIES"] = [QuotaIncreasePolicy()]
    app_config["RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE"] = 50 * 10**9
    return app_config


def test_quota_increase_with_non_integer_pid(
    running_app, minimal_record, uploader, location
):
    """Quota increase works with the default (non-integer) record identifiers."""
    draft = records_service.create(uploader.identity, minimal_record)
    assert not draft.id.isdigit()  # the default provider mints alphanumeric ids

    records_service.quota_increase(uploader.identity, draft.id, {"quota_size": "10"})

    draft = records_service.read_draft(uploader.identity, draft.id)
    assert draft._record.files.bucket.quota_size == 10 * 10**9
