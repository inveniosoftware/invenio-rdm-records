# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test Crossref additional prefix handling for parent DOIs."""

import pytest
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.resources.serializers import (
    CrossrefXMLSerializer,
    DataCite45JSONSerializer,
)
from invenio_rdm_records.services.pids import providers
from tests.fake_crossref_client import FakeCrossrefClient
from tests.fake_datacite_client import FakeDataCiteClient


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override app_config to add Crossref provider with additional prefixes."""
    fake_datacite = FakeDataCiteClient("datacite", config_prefix="DATACITE")
    fake_crossref = FakeCrossrefClient("crossref", config_prefix="CROSSREF")

    app_config["CROSSREF_ENABLED"] = True
    app_config["CROSSREF_PREFIX"] = "10.59350"
    app_config["CROSSREF_ADDITIONAL_PREFIXES"] = ["10.65527"]
    app_config["CROSSREF_USERNAME"] = "test_user"
    app_config["CROSSREF_PASSWORD"] = "test_pass"
    app_config["CROSSREF_DEPOSITOR"] = "Test Depositor"
    app_config["CROSSREF_EMAIL"] = "test@example.com"
    app_config["CROSSREF_REGISTRANT"] = "Test Registrant"
    app_config["CROSSREF_TEST_MODE"] = True
    app_config["SITE_UI_URL"] = "https://example.org"

    app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        providers.DataCitePIDProvider(
            "datacite",
            client=fake_datacite,
            label=_("DOI"),
        ),
        providers.CrossrefPIDProvider(
            "crossref",
            client=fake_crossref,
            label=_("DOI"),
        ),
        providers.ExternalPIDProvider(
            "external",
            "doi",
            validators=[
                providers.BlockedPrefixes(
                    config_names=[
                        "DATACITE_PREFIX",
                        "CROSSREF_PREFIX",
                    ]
                )
            ],
            label=_("DOI"),
        ),
        providers.OAIPIDProvider(
            "oai",
            label=_("OAI ID"),
        ),
    ]

    app_config["RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        providers.DataCitePIDProvider(
            "datacite",
            client=fake_datacite,
            serializer=DataCite45JSONSerializer(is_parent=True),
            label=_("Concept DOI"),
        ),
        providers.CrossrefPIDProvider(
            "crossref",
            client=fake_crossref,
            serializer=CrossrefXMLSerializer(),
            label=_("Concept DOI"),
        ),
    ]

    app_config["RDM_PERSISTENT_IDENTIFIERS"] = {
        "doi": {
            "providers": ["datacite", "crossref", "external"],
            "required": True,
            "label": _("DOI"),
            "validator": lambda x: True,
            "normalizer": lambda x: x.lower(),
            "is_enabled": lambda app: True,
            "ui": {"default_selected": "yes"},
        },
        "oai": {
            "providers": ["oai"],
            "required": True,
            "label": _("OAI"),
            "is_enabled": lambda app: True,
        },
    }

    app_config["RDM_PARENT_PERSISTENT_IDENTIFIERS"] = {
        "doi": {
            "providers": ["datacite", "crossref"],
            "required": True,
            "condition": lambda rec: rec.pids.get("doi", {}).get("provider")
            in ("datacite", "crossref"),
            "label": _("Concept DOI"),
            "validator": lambda x: True,
            "normalizer": lambda x: x.lower(),
            "is_enabled": lambda app: True,
        },
    }

    return app_config


@pytest.fixture()
def service(running_app):
    """Service fixture."""
    return current_rdm_records.records_service


def test_crossref_additional_prefix_parent_doi(
    running_app,
    search_clear,
    minimal_record,
    identity_simple,
    service,
    location,
):
    """Test that parent DOI uses same additional Crossref prefix as child.

    Scenario:
    1. Create draft with Crossref DOI using additional prefix (10.65527)
    2. Publish the record
    3. Verify parent DOI also uses the additional prefix (10.65527), not default (10.59350)
    """
    # Create a draft with Crossref DOI using additional prefix
    minimal_record["metadata"]["resource_type"]["id"] = "publication-preprint"
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.65527/test.1234",
            "provider": "crossref",
            "client": "crossref",
        }
    }

    draft = service.create(identity_simple, minimal_record)
    assert draft.id

    # Verify draft has the custom prefix DOI
    draft_doi = draft["pids"]["doi"]
    assert draft_doi["identifier"] == "10.65527/test.1234"
    assert draft_doi["provider"] == "crossref"
    # Prefix is derived from identifier, not stored as a separate field
    assert draft_doi["identifier"].startswith("10.65527/")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    # Check child record DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["identifier"] == "10.65527/test.1234"
    assert child_doi["provider"] == "crossref"

    # Check parent record DOI - should use same prefix as child
    print(record["parent"]["pids"])
    parent_doi = record["parent"]["pids"]["doi"]

    # Parent DOI was enabled via RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS
    assert parent_doi is not None, "Parent DOI should be created for Crossref record"
    assert "identifier" in parent_doi, "Parent DOI should have identifier"
    parent_prefix = parent_doi["identifier"].split("/")[0]
    assert (
        parent_prefix == "10.65527"
    ), f"Parent DOI prefix {parent_prefix} should match child prefix 10.65527"
    assert parent_doi["provider"] == "crossref"

    # Verify in database
    child_pid = PersistentIdentifier.get("doi", "10.65527/test.1234")
    assert child_pid.status == PIDStatus.REGISTERED
    assert child_pid.pid_provider == "crossref"


def test_crossref_republish_with_additional_prefix(
    running_app,
    search_clear,
    minimal_record,
    identity_simple,
    service,
    location,
):
    """Test republishing a record with additional Crossref prefix.

    This tests the scenario where:
    1. Record is published with additional prefix
    2. New draft is created (edit)
    3. Draft is published again
    4. Should not get "PID already exists" error
    """
    # Create and publish initial version
    minimal_record["metadata"]["resource_type"]["id"] = "publication-preprint"
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.65527/test.5678",
            "provider": "crossref",
            "client": "crossref",
        }
    }

    draft = service.create(identity_simple, minimal_record)
    record = service.publish(identity_simple, draft.id)

    assert record["pids"]["doi"]["identifier"] == "10.65527/test.5678"

    # Create new draft (edit)
    draft2 = service.edit(identity_simple, record.id)
    assert draft2.id

    # Verify draft still has correct DOI
    assert draft2["pids"]["doi"]["identifier"] == "10.65527/test.5678"
    assert draft2["pids"]["doi"]["provider"] == "crossref"

    # Republish - this should NOT raise "PID already exists" error
    record2 = service.publish(identity_simple, draft2.id)

    assert record2["pids"]["doi"]["identifier"] == "10.65527/test.5678"
    assert record2["pids"]["doi"]["provider"] == "crossref"
    print(record2["parent"]["pids"])
    parent_doi = record2["parent"]["pids"]["doi"]
    assert parent_doi is not None, "Parent DOI should exist after republish"
    assert "identifier" in parent_doi
    parent_prefix = parent_doi["identifier"].split("/")[0]
    assert parent_prefix == "10.65527"


def test_crossref_default_vs_additional_prefix(
    running_app,
    search_clear,
    minimal_record,
    identity_simple,
    service,
    location,
):
    """Test that default and additional prefixes are handled correctly.

    Creates two records:
    1. One with default prefix (10.59350)
    2. One with additional prefix (10.65527)

    Both should work without conflicts.
    """
    # Record with default prefix
    minimal_record["metadata"]["resource_type"]["id"] = "publication-preprint"
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.59350/default.001",
            "provider": "crossref",
            "client": "crossref",
        }
    }

    draft1 = service.create(identity_simple, minimal_record)
    record1 = service.publish(identity_simple, draft1.id)
    assert record1["pids"]["doi"]["identifier"] == "10.59350/default.001"

    # Record with additional prefix
    minimal_record["metadata"]["resource_type"]["id"] = "publication-preprint"
    minimal_record["metadata"]["title"] = "Different Record"
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.65527/additional.001",
            "provider": "crossref",
            "client": "crossref",
        }
    }

    draft2 = service.create(identity_simple, minimal_record)
    record2 = service.publish(identity_simple, draft2.id)
    assert record2["pids"]["doi"]["identifier"] == "10.65527/additional.001"

    # Both should exist independently
    pid1 = PersistentIdentifier.get("doi", "10.59350/default.001")
    pid2 = PersistentIdentifier.get("doi", "10.65527/additional.001")

    assert pid1.status == PIDStatus.REGISTERED
    assert pid2.status == PIDStatus.REGISTERED
    assert pid1.object_uuid != pid2.object_uuid
