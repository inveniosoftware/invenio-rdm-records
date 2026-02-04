# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test that parent DOI uses same provider and prefix as child record."""

import pytest
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.pids import providers
from tests.fake_crossref_client import FakeCrossrefClient


@pytest.fixture()
def crossref_config(running_app):
    """Configure Crossref for tests."""
    # Set Crossref config values
    running_app.app.config["CROSSREF_ENABLED"] = True
    running_app.app.config["CROSSREF_USERNAME"] = "INVALID"
    running_app.app.config["CROSSREF_PASSWORD"] = "INVALID"
    running_app.app.config["CROSSREF_DEPOSITOR"] = "INVALID"
    running_app.app.config["CROSSREF_EMAIL"] = "info@example.org"
    running_app.app.config["CROSSREF_REGISTRANT"] = "INVALID"
    running_app.app.config["CROSSREF_PREFIX"] = "10.1234"

    # Add Crossref provider to the list of providers
    providers_list = running_app.app.config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"]
    providers_list.append(
        providers.CrossrefPIDProvider(
            "crossref",
            client=FakeCrossrefClient("crossref", config_prefix="CROSSREF"),
            label=_("DOI"),
        )
    )

    # Also add to parent providers
    parent_providers_list = running_app.app.config[
        "RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS"
    ]
    parent_providers_list.append(
        providers.CrossrefPIDProvider(
            "crossref",
            client=FakeCrossrefClient("crossref", config_prefix="CROSSREF"),
            label=_("Concept DOI"),
        )
    )
    yield


def test_parent_doi_uses_child_provider_crossref(
    running_app, minimal_record, superuser_identity, crossref_config
):
    """Test that parent DOI uses same Crossref provider and prefix as child."""
    # Enable crossref provider
    running_app.app.config["RDM_PERSISTENT_IDENTIFIERS"]["doi"]["providers"] = [
        "crossref",
        "external",
    ]

    service = current_rdm_records.records_service

    # Create draft first (without PIDs)
    data = minimal_record.copy()
    draft = service.create(superuser_identity, data)

    # Set the custom Crossref prefix in PIDs by accessing internal draft
    # We need to set prefix in draft.pids before calling pids.create()
    from invenio_rdm_records.records.api import RDMDraft

    draft_record = RDMDraft.pid.resolve(draft.id, registered_only=False)
    draft_record.pids = {"doi": {"provider": "crossref", "prefix": "10.7777"}}
    draft_record.commit()

    # Now create the DOI
    draft = service.pids.create(
        superuser_identity, draft.id, "doi", provider="crossref"
    )

    # Publish the record
    record = service.publish(superuser_identity, draft.id)

    # Check child DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["provider"] == "crossref"
    assert child_doi["identifier"].startswith(
        "10.7777/"
    ), f"Child DOI should use custom prefix: {child_doi['identifier']}"

    # Check parent DOI
    parent_doi = record["parent"]["pids"]["doi"]
    assert (
        parent_doi["provider"] == "crossref"
    ), "Parent DOI should use same provider as child"
    assert parent_doi["identifier"].startswith(
        "10.7777/"
    ), f"Parent DOI should use same prefix as child: {parent_doi['identifier']}"


def test_parent_doi_uses_child_provider_datacite(
    running_app, minimal_record, superuser_identity
):
    """Test that parent DOI uses same DataCite provider and prefix as child."""
    service = current_rdm_records.records_service

    # Create draft first (without PIDs)
    data = minimal_record.copy()
    draft = service.create(superuser_identity, data)

    # Set the custom DataCite prefix in PIDs
    draft_data = draft.to_dict()
    draft_data["pids"] = {
        "doi": {
            "provider": "datacite",
            "prefix": "10.9999",  # Custom prefix
        }
    }
    draft = service.update_draft(superuser_identity, draft.id, draft_data)

    # Now create the DOI
    draft = service.pids.create(superuser_identity, draft.id, "doi")

    # Publish the record
    record = service.publish(superuser_identity, draft.id)

    # Check child DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["provider"] == "datacite"
    assert child_doi["identifier"].startswith(
        "10.9999/"
    ), f"Child DOI should use custom prefix: {child_doi['identifier']}"

    # Check parent DOI
    parent_doi = record["parent"]["pids"]["doi"]
    assert (
        parent_doi["provider"] == "datacite"
    ), "Parent DOI should use same provider as child"
    assert parent_doi["identifier"].startswith(
        "10.9999/"
    ), f"Parent DOI should use same prefix as child: {parent_doi['identifier']}"

    # Verify both DOIs exist in PIDStore with correct status
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    child_pid = provider.get(pid_value=child_doi["identifier"])
    assert child_pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]

    parent_pid = provider.get(pid_value=parent_doi["identifier"])
    assert parent_pid.status in [PIDStatus.RESERVED, PIDStatus.REGISTERED]


def test_parent_doi_default_provider_and_prefix(
    running_app, minimal_record, superuser_identity
):
    """Test that parent DOI uses default provider/prefix when child has none specified."""
    service = current_rdm_records.records_service

    # Create draft without explicit provider/prefix (uses defaults)
    data = minimal_record.copy()
    draft = service.create(superuser_identity, data)

    # No need to set PIDs - just create DOI with defaults
    draft = service.pids.create(superuser_identity, draft.id, "doi")

    # Publish the record
    record = service.publish(superuser_identity, draft.id)

    # Check child DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["provider"] == "datacite"  # Default provider
    assert child_doi["identifier"].startswith("10.1234/")  # Default DATACITE_PREFIX

    # Check parent DOI
    parent_doi = record["parent"]["pids"]["doi"]
    assert (
        parent_doi["provider"] == "datacite"
    ), "Parent should use same default provider"
    assert parent_doi["identifier"].startswith(
        "10.1234/"
    ), "Parent should use same default prefix"


def test_parent_doi_consistency_across_versions(
    running_app, minimal_record, superuser_identity
):
    """Test that parent DOI stays consistent across versions."""
    service = current_rdm_records.records_service

    # Create and publish first version with custom prefix
    data = minimal_record.copy()
    draft = service.create(superuser_identity, data)

    # Set custom prefix
    draft_data = draft.to_dict()
    draft_data["pids"] = {"doi": {"provider": "datacite", "prefix": "10.8888"}}
    draft = service.update_draft(superuser_identity, draft.id, draft_data)

    # Create DOI
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    record_v1 = service.publish(superuser_identity, draft.id)

    # Get parent DOI from first version
    parent_doi_v1 = record_v1["parent"]["pids"]["doi"]["identifier"]
    assert parent_doi_v1.startswith("10.8888/")

    # Create second version
    draft_v2 = service.new_version(superuser_identity, record_v1.id)
    draft_v2 = service.pids.create(superuser_identity, draft_v2.id, "doi")

    # Update metadata for v2
    from copy import deepcopy

    data_v2 = deepcopy(draft_v2.data)
    data_v2["metadata"]["title"] = "Updated Title"
    draft_v2 = service.update_draft(superuser_identity, draft_v2.id, data_v2)

    # Publish v2
    record_v2 = service.publish(superuser_identity, draft_v2.id)

    # Parent DOI should be the same across versions
    parent_doi_v2 = record_v2["parent"]["pids"]["doi"]["identifier"]
    assert (
        parent_doi_v2 == parent_doi_v1
    ), "Parent DOI should remain the same across versions"

    # Child DOIs should be different
    child_doi_v1 = record_v1["pids"]["doi"]["identifier"]
    child_doi_v2 = record_v2["pids"]["doi"]["identifier"]
    assert (
        child_doi_v1 != child_doi_v2
    ), "Child DOIs should be different for different versions"

    # Both child DOIs should use the same prefix
    assert child_doi_v1.startswith("10.8888/")
    assert child_doi_v2.startswith("10.8888/")
