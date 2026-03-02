# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_i18n import lazy_gettext as _

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.pids import providers
from tests.fake_crossref_client import FakeCrossrefClient


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override app_config to add Crossref provider for tests."""
    # Add Crossref provider to the list
    app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=providers.DataCiteClient("datacite", config_prefix="DATACITE"),
            label=_("DOI"),
        ),
        # Crossref DOI provider with fake client
        providers.CrossrefPIDProvider(
            "crossref",
            client=FakeCrossrefClient("crossref", config_prefix="CROSSREF"),
            label=_("DOI"),
        ),
        # DOI provider for externally managed DOIs
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
        # OAI identifier
        providers.OAIPIDProvider(
            "oai",
            label=_("OAI ID"),
        ),
    ]

    # Add Crossref to the DOI providers list
    app_config["RDM_PERSISTENT_IDENTIFIERS"] = {
        "doi": {
            "providers": ["datacite", "crossref", "external"],
            "required": True,
            "label": _("DOI"),
            "is_enabled": lambda app: True,
        },
        "oai": {
            "providers": ["oai"],
            "required": True,
            "label": _("OAI"),
            "is_enabled": lambda app: True,
        },
    }

    # Enable Crossref for tests
    app_config["CROSSREF_ENABLED"] = True
    app_config["CROSSREF_USERNAME"] = "test_username"
    app_config["CROSSREF_PASSWORD"] = "test_password"
    app_config["CROSSREF_PREFIX"] = "10.5555"
    app_config["CROSSREF_DEPOSITOR"] = "Test Depositor"
    app_config["CROSSREF_EMAIL"] = "test@example.com"
    app_config["CROSSREF_REGISTRANT"] = "Test Institution"

    return app_config


@pytest.fixture(scope="function")
def record(app, location, db, superuser_identity, minimal_record):
    """Application factory fixture."""
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    record_ = service.publish(draft.id, superuser_identity)

    return record_
