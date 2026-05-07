# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 University of Münster.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests reproducing 'A PID already exists for type doi' error on republish.

These tests verify that editing and republishing a record with a Crossref DOI
does NOT raise a 'PID already exists' validation error. Two scenarios are
tested:
1. DOI with a prefix from CROSSREF_ADDITIONAL_PREFIXES
2. DOI with the main CROSSREF_PREFIX
"""

import pytest
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.resources.serializers import DataCite45JSONSerializer
from invenio_rdm_records.services.pids import providers
from tests.fake_crossref_client import FakeCrossrefClient
from tests.fake_datacite_client import FakeDataCiteClient


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override app_config to add Crossref provider with additional prefixes.

    This builds on top of the base app_config from conftest.py, adding
    Crossref support (provider, client, config variables).
    """
    fake_datacite = FakeDataCiteClient("datacite", config_prefix="DATACITE")
    fake_crossref = FakeCrossrefClient("crossref", config_prefix="CROSSREF")

    # Enable Crossref with main prefix + additional prefix
    app_config["CROSSREF_ENABLED"] = True
    app_config["CROSSREF_USERNAME"] = "test_user"
    app_config["CROSSREF_PASSWORD"] = "test_pass"
    app_config["CROSSREF_PREFIX"] = "10.59350"
    app_config["CROSSREF_ADDITIONAL_PREFIXES"] = ["10.65527"]
    app_config["CROSSREF_DEPOSITOR"] = "Test Depositor"
    app_config["CROSSREF_EMAIL"] = "test@example.com"
    app_config["CROSSREF_REGISTRANT"] = "Test Registrant"
    app_config["CROSSREF_TEST_MODE"] = True

    # Register all PID providers including Crossref
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

    # Parent PID providers (DataCite only for concept DOI)
    app_config["RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        providers.DataCitePIDProvider(
            "datacite",
            client=fake_datacite,
            serializer=DataCite45JSONSerializer(is_parent=True),
            label=_("Concept DOI"),
        ),
    ]

    # Include crossref in DOI providers list
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

    return app_config


@pytest.fixture()
def service(running_app):
    """Service fixture."""
    return current_rdm_records.records_service


def test_republish_crossref_additional_prefix(
    running_app,
    search_clear,
    minimal_record,
    identity_simple,
    service,
    location,
):
    """Reproduce 'PID already exists' error on republish with additional prefix.

    Scenario:
    1. Create draft with Crossref DOI using additional prefix (10.65527)
    2. Publish the record
    3. Edit the record (creates new draft)
    4. Republish → should NOT raise 'A PID already exists for type doi'
    """
    # --- Step 1: Create draft with additional-prefix Crossref DOI ---
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.65527/republish.additional.001",
            "provider": "crossref",
            "client": "crossref",
        }
    }

    draft = service.create(identity_simple, minimal_record)
    assert draft["pids"]["doi"]["identifier"] == "10.65527/republish.additional.001"
    assert draft["pids"]["doi"]["provider"] == "crossref"

    # --- Step 2: Publish ---
    record = service.publish(identity_simple, draft.id)
    assert record["pids"]["doi"]["identifier"] == "10.65527/republish.additional.001"
    assert record["pids"]["doi"]["provider"] == "crossref"

    # Verify PID in database
    pid = PersistentIdentifier.get("doi", "10.65527/republish.additional.001")
    assert pid.status == PIDStatus.REGISTERED
    assert pid.pid_provider == "crossref"

    # --- Step 3: Edit (creates new draft from published record) ---
    draft2 = service.edit(identity_simple, record.id)
    assert draft2["pids"]["doi"]["identifier"] == "10.65527/republish.additional.001"
    assert draft2["pids"]["doi"]["provider"] == "crossref"

    # --- Step 4: Republish ---
    # This should NOT raise ValidationError("A PID already exists for type doi")
    record2 = service.publish(identity_simple, draft2.id)

    assert record2["pids"]["doi"]["identifier"] == "10.65527/republish.additional.001"
    assert record2["pids"]["doi"]["provider"] == "crossref"

    # PID should still be registered, pointing to same record
    pid2 = PersistentIdentifier.get("doi", "10.65527/republish.additional.001")
    assert pid2.status == PIDStatus.REGISTERED


def test_republish_crossref_main_prefix(
    running_app,
    search_clear,
    minimal_record,
    identity_simple,
    service,
    location,
):
    """Reproduce 'PID already exists' error on republish with main prefix.

    Scenario:
    1. Create draft with Crossref DOI using main prefix (CROSSREF_PREFIX = 10.59350)
    2. Publish the record
    3. Edit the record (creates new draft)
    4. Republish → should NOT raise 'A PID already exists for type doi'
    """
    # --- Step 1: Create draft with main-prefix Crossref DOI ---
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.59350/republish.main.001",
            "provider": "crossref",
            "client": "crossref",
        }
    }

    draft = service.create(identity_simple, minimal_record)
    assert draft["pids"]["doi"]["identifier"] == "10.59350/republish.main.001"
    assert draft["pids"]["doi"]["provider"] == "crossref"

    # --- Step 2: Publish ---
    record = service.publish(identity_simple, draft.id)
    assert record["pids"]["doi"]["identifier"] == "10.59350/republish.main.001"
    assert record["pids"]["doi"]["provider"] == "crossref"

    # Verify PID in database
    pid = PersistentIdentifier.get("doi", "10.59350/republish.main.001")
    assert pid.status == PIDStatus.REGISTERED
    assert pid.pid_provider == "crossref"

    # --- Step 3: Edit (creates new draft from published record) ---
    draft2 = service.edit(identity_simple, record.id)
    assert draft2["pids"]["doi"]["identifier"] == "10.59350/republish.main.001"
    assert draft2["pids"]["doi"]["provider"] == "crossref"

    # --- Step 4: Republish ---
    # This should NOT raise ValidationError("A PID already exists for type doi")
    record2 = service.publish(identity_simple, draft2.id)

    assert record2["pids"]["doi"]["identifier"] == "10.59350/republish.main.001"
    assert record2["pids"]["doi"]["provider"] == "crossref"

    # PID should still be registered, pointing to same record
    pid2 = PersistentIdentifier.get("doi", "10.59350/republish.main.001")
    assert pid2.status == PIDStatus.REGISTERED
