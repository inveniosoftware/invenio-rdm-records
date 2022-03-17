# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Funder resource tests."""


def test_funders_get(client, example_funder, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_funder.id

    res = client.get(f"/funders/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/funders/01ggx4157"
    }


def test_funders_search(client, example_funder, headers):
    """Test a successful search."""
    res = client.get("/funders", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"
