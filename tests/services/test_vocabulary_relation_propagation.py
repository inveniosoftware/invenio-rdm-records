# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Vocabulary update propagation to referencing records."""

from copy import deepcopy

from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation

from invenio_rdm_records.proxies import current_rdm_records_service as records_service


def test_affiliation_update_reindexes_referencing_records(
    running_app, minimal_record, affiliations_v
):
    """Updating an affiliation reindexes records that reference it."""
    # Create and publish a record that references the affiliation
    data = deepcopy(minimal_record)
    data["metadata"]["creators"][0]["affiliations"] = [{"id": "cern"}]
    draft = records_service.create(system_identity, data)
    record = records_service.publish(system_identity, draft.id)
    records_service.record_cls.index.refresh()

    hits = records_service.search(system_identity, {"q": f"id:{record.id}"})
    assert hits.total == 1
    hit = list(hits.hits)[0]
    assert hit["metadata"]["creators"][0]["affiliations"][0]["name"] == "CERN"

    # Update the affiliation vocabulary entry (triggers change notification)
    affiliations_service = current_service_registry.get("affiliations")
    updated = {
        "id": "cern",
        "name": "CERN Updated",
        "acronym": "CERN",
        "identifiers": affiliations_v["identifiers"],
    }
    affiliations_service.update(system_identity, "cern", updated)
    Affiliation.index.refresh()

    # Change-notification task queues a reindex; drain the indexer
    success, errors = records_service.indexer.process_bulk_queue()
    assert success >= 1
    assert errors == 0
    records_service.record_cls.index.refresh()

    hits = records_service.search(system_identity, {"q": f"id:{record.id}"})
    assert hits.total == 1
    hit = list(hits.hits)[0]
    assert hit["metadata"]["creators"][0]["affiliations"][0]["name"] == "CERN Updated"
