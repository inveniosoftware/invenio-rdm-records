# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Unmanaged provider tests."""

from flask_babelex import lazy_gettext as _

from invenio_rdm_records.services.pids.providers import UnmanagedPIDProvider


def test_unmanaged_provider_validate(app, db):
    provider = UnmanagedPIDProvider(pid_type="testid")
    success, errors = provider.validate(provider="unmanaged")
    assert success
    assert not errors


def test_unmanaged_provider_validate_failure(app, db):
    provider = UnmanagedPIDProvider(pid_type="testid")
    success, errors = provider.validate(client="someclient", provider="fail")

    expected_errors = [
        _("Provider name fail does not match unmanaged"),
        _("Client attribute not supported for provider unmanaged")
    ]
    assert not success
    assert errors == expected_errors
