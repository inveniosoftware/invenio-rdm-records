# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Resource access tokens feature flag."""

import pytest


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config["RDM_RESOURCE_ACCESS_TOKENS_ENABLED"] = False
    return app_config


def test_rat_feature_disabled(running_app, client, uploader):
    """Test feature flag RDM_RESOURCE_ACCESS_TOKENS_ENABLED = False."""
    record_owner = uploader.login(client)
    record_file_url = "/records/recid/files/test.pdf/content"
    res = record_owner.get(
        record_file_url, query_string={"resource_access_token": "bla"}
    )

    assert res.status_code == 400
    assert (
        res.json["message"] == "Resource Access Tokens feature is currently disabled."
    )
