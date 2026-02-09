# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test that parent DOI uses same provider and prefix as child record."""

import pytest
from invenio_i18n import lazy_gettext as _

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
    """Override app_config to include Crossref provider."""
    fake_datacite = FakeDataCiteClient("datacite", config_prefix="DATACITE")
    fake_crossref = FakeCrossrefClient("crossref", config_prefix="CROSSREF")

    app_config["CROSSREF_ENABLED"] = True
    app_config["CROSSREF_USERNAME"] = "INVALID"
    app_config["CROSSREF_PASSWORD"] = "INVALID"
    app_config["CROSSREF_DEPOSITOR"] = "INVALID"
    app_config["CROSSREF_EMAIL"] = "info@example.org"
    app_config["CROSSREF_REGISTRANT"] = "INVALID"
    app_config["CROSSREF_PREFIX"] = "10.1234"

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
                    config_names=["DATACITE_PREFIX", "CROSSREF_PREFIX"]
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

    return app_config


@pytest.fixture()
def service(running_app):
    """Service fixture."""
    return current_rdm_records.records_service


def test_parent_doi_uses_child_provider_crossref(
    running_app, search_clear, minimal_record, superuser_identity, service, location
):
    """Test that parent DOI uses same Crossref provider and prefix as child."""
    # Create draft with a Crossref DOI identifier (prefix is implicit in the identifier)
    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.1234/crossref.parent.test1",
            "provider": "crossref",
            "client": "crossref",
        }
    }
    draft = service.create(superuser_identity, minimal_record)

    # Publish the record
    record = service.publish(superuser_identity, draft.id)

    # Check child DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["provider"] == "crossref"
    assert child_doi["identifier"] == "10.1234/crossref.parent.test1"


def test_parent_doi_uses_child_provider_datacite(
    running_app, search_clear, minimal_record, superuser_identity, service, location
):
    """Test that parent DOI uses DataCite provider by default."""
    # Create draft without explicit DOI - DataCite creates one automatically
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")

    # Publish the record
    record = service.publish(superuser_identity, draft.id)

    # Check child DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["provider"] == "datacite"
    assert child_doi["identifier"].startswith("10.1234/")

    # Check parent DOI
    parent_doi = record["parent"]["pids"]["doi"]
    assert parent_doi["provider"] == "datacite"
    assert parent_doi["identifier"].startswith("10.1234/")


def test_parent_doi_default_provider_and_prefix(
    running_app, search_clear, minimal_record, superuser_identity, service, location
):
    """Test that parent DOI uses default provider/prefix when child has none specified."""
    # Create draft without explicit provider/prefix (uses defaults)
    draft = service.create(superuser_identity, minimal_record)

    # Create DOI with defaults
    draft = service.pids.create(superuser_identity, draft.id, "doi")

    # Publish the record
    record = service.publish(superuser_identity, draft.id)

    # Check child DOI
    child_doi = record["pids"]["doi"]
    assert child_doi["provider"] == "datacite"
    assert child_doi["identifier"].startswith("10.1234/")

    # Check parent DOI
    parent_doi = record["parent"]["pids"]["doi"]
    assert parent_doi["provider"] == "datacite"
    assert parent_doi["identifier"].startswith("10.1234/")


def test_parent_doi_consistency_across_versions(
    running_app, search_clear, minimal_record, superuser_identity, service, location
):
    """Test that parent DOI stays consistent across versions."""
    from copy import deepcopy

    # Create and publish first version
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    record_v1 = service.publish(superuser_identity, draft.id)

    # Get parent DOI from first version
    parent_doi_v1 = record_v1["parent"]["pids"]["doi"]["identifier"]
    assert parent_doi_v1.startswith("10.1234/")

    # Create second version
    draft_v2 = service.new_version(superuser_identity, record_v1.id)
    draft_v2 = service.pids.create(superuser_identity, draft_v2.id, "doi")

    # Update metadata for v2
    data_v2 = deepcopy(draft_v2.data)
    data_v2["metadata"]["title"] = "Updated Title"
    data_v2["metadata"]["publication_date"] = "2020-06-01"
    draft_v2 = service.update_draft(superuser_identity, draft_v2.id, data_v2)

    # Publish v2
    record_v2 = service.publish(superuser_identity, draft_v2.id)

    # Parent DOI should be the same across versions
    parent_doi_v2 = record_v2["parent"]["pids"]["doi"]["identifier"]
    assert parent_doi_v2 == parent_doi_v1

    # Child DOIs should be different
    child_doi_v1 = record_v1["pids"]["doi"]["identifier"]
    child_doi_v2 = record_v2["pids"]["doi"]["identifier"]
    assert child_doi_v1 != child_doi_v2

    # Both child DOIs should use the same prefix
    assert child_doi_v1.startswith("10.1234/")
    assert child_doi_v2.startswith("10.1234/")
