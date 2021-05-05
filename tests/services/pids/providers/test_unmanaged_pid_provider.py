# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Unmanaged provider tests."""

import pytest
from flask_babelex import lazy_gettext as _

from invenio_rdm_records.services.pids.providers import UnmanagedPIDProvider


@pytest.fixture(scope='function')
def unmananged_provider():
    """Application factory fixture."""
    return UnmanagedPIDProvider(pid_type="testid")


def test_unmanaged_provider_validate(
    running_app, db, unmananged_provider, record
):
    success, errors = unmananged_provider.validate(
        record=record, provider="unmanaged")
    assert success
    assert not errors


def test_unmanaged_provider_validate_failure(
    running_app, db, unmananged_provider, record
):
    success, errors = unmananged_provider.validate(
        record=record, client="someclient", provider="fail")

    expected_errors = [
        _("Provider name fail does not match unmanaged"),
        _("Client attribute not supported for provider unmanaged")
    ]
    assert not success
    assert errors == expected_errors
