# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

from copy import deepcopy

import pytest
from invenio_pidstore.models import PersistentIdentifier

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import ValidationErrorWithMessageAsList

DOI = "10.5555/duplicate.doi.001"


@pytest.fixture()
def service(running_app):
    return current_rdm_records.records_service


def _create_draft_with_doi(service, identity, minimal_record, title):
    """Create a draft for a new record claiming the shared DOI."""
    data = deepcopy(minimal_record)
    data["metadata"]["title"] = title
    data["pids"] = {
        "doi": {"identifier": DOI, "provider": "crossref", "client": "crossref"}
    }
    return service.create(identity, data)


def test_crossref_doi_cannot_be_duplicated(
    running_app, search_clear, minimal_record, identity_simple, service, location
):
    error_msg = {"field": "pids.doi", "messages": [f"doi:{DOI} already exists."]}

    # First record claims the DOI and publishes fine.
    draft1 = _create_draft_with_doi(
        service, identity_simple, minimal_record, "First record"
    )
    record1 = service.publish(identity_simple, draft1.id)

    assert not draft1.errors
    assert record1["pids"]["doi"]["identifier"] == DOI

    # A different record tries to reuse the same DOI.
    draft2 = _create_draft_with_doi(
        service, identity_simple, minimal_record, "Second record"
    )

    assert error_msg in draft2.errors

    # publishing must be refused.
    with pytest.raises(ValidationErrorWithMessageAsList) as exc_info:
        service.publish(identity_simple, draft2.id)
    assert error_msg in exc_info.value.messages

    # The DOI still belongs to the first record.
    pid = PersistentIdentifier.get("doi", DOI)

    assert pid.object_uuid == record1._record.id
