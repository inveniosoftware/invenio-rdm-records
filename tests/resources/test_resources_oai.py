# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz Univeresity of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH resource level tests."""

import pytest
from flask import current_app
from invenio_oaiserver.errors import OAISetSpecUpdateError


def _create_set(client, data, headers, status_code):
    """Send POST request."""
    s = client.post(
        '/oaipmh/sets',
        headers=headers,
        json=data,
    )
    assert s.status_code == status_code
    return s


def _get_set(client, id, headers, status_code):
    """Send GET request."""
    s = client.get(
        f'/oaipmh/sets/{id}',
        headers=headers,
    )
    assert s.status_code == status_code
    return s


def _update_set(client, id, data, headers, status_code):
    """Send PUT request."""
    s = client.put(
        f'/oaipmh/sets/{id}',
        headers=headers,
        json=data,
    )
    assert s.status_code == status_code
    return s


def _delete_set(client, id, headers, status_code):
    """Send DELETE request."""
    s = client.delete(
        f'/oaipmh/sets/{id}',
        headers=headers,
    )
    assert s.status_code == status_code
    return s


def _search_sets(client, query, headers, status_code):
    s = client.get(
        '/oaipmh/sets',
        headers=headers,
        query_string=query,
    )
    assert s.status_code == status_code
    return s


def _search_formats(client, headers, status_code):
    s = client.get(
        '/oaipmh/formats',
        headers=headers,
    )
    assert s.status_code == status_code
    return s


def test_create_set(client, admin, minimal_oai_set, headers):
    """Create a set."""
    client = admin.login(client)

    # without description
    s1 = _create_set(client, minimal_oai_set, headers, 201).json
    assert s1["name"] == minimal_oai_set["name"]
    assert s1["spec"] == minimal_oai_set["spec"]
    assert s1["description"] == minimal_oai_set["description"]
    assert s1["search_pattern"] == minimal_oai_set["search_pattern"]

    # with description
    minimal_oai_set["spec"] = "s2"
    minimal_oai_set["description"] = "description"
    s2 = _create_set(client, minimal_oai_set, headers, 201).json
    assert s2["name"] == minimal_oai_set["name"]
    assert s2["spec"] == minimal_oai_set["spec"]
    assert s2["description"] == minimal_oai_set["description"]
    assert s2["search_pattern"] == minimal_oai_set["search_pattern"]

    valid = ["-", "_", ".", "!", "~", "*", "'", "(", ")"]
    for vs in valid:
        s = minimal_oai_set.copy()
        s["spec"] = vs
        cs = _create_set(client, s, headers, 201).json
        assert s["spec"] == cs["spec"]


def test_create_set_duplicate(client, admin, minimal_oai_set, headers):
    """Create two sets with same spec."""
    client = admin.login(client)

    _create_set(client, minimal_oai_set, headers, 201)
    _create_set(client, minimal_oai_set, headers, 400)


def test_create_set_invalid_data(client, admin, minimal_oai_set, headers):
    """Try to create a set with invalid params."""
    client = admin.login(client)

    key = "name"
    s = minimal_oai_set.copy()
    s[key] *= 256
    _create_set(client, s, headers, 400)
    del s[key]
    _create_set(client, s, headers, 400)

    key = "spec"
    s = minimal_oai_set.copy()
    s[key] *= 256
    _create_set(client, s, headers, 400)
    del s[key]
    _create_set(client, s, headers, 400)

    invalid = [";", "/", "?", ":", "@", "&", "=", "+", "$", ",", "community-"]
    for ivs in invalid:
        s = minimal_oai_set.copy()
        s["spec"] = ivs
        _create_set(client, s, headers, 400).json

    key = "search_pattern"
    s = minimal_oai_set.copy()
    del s[key]
    _create_set(client, s, headers, 400)


def test_get_set(client, admin, minimal_oai_set, headers):
    """Retrieve a set."""
    client = admin.login(client)

    # without description
    created_set = _create_set(client, minimal_oai_set, headers, 201).json
    retrieved_set = _get_set(client, created_set["id"], headers, 200).json
    assert created_set["id"] == retrieved_set["id"]
    assert created_set["name"] == retrieved_set["name"]
    assert created_set["spec"] == retrieved_set["spec"]
    assert created_set["description"] == retrieved_set["description"]
    assert created_set["search_pattern"] == retrieved_set["search_pattern"]

    # with description
    minimal_oai_set["spec"] = "s2"
    minimal_oai_set["description"] = "description"
    created_set = _create_set(client, minimal_oai_set, headers, 201).json
    retrieved_set = _get_set(client, created_set["id"], headers, 200).json
    assert created_set["id"] == retrieved_set["id"]
    assert created_set["name"] == retrieved_set["name"]
    assert created_set["spec"] == retrieved_set["spec"]
    assert created_set["description"] == retrieved_set["description"]


def test_get_set_not_existing(client, admin, headers):
    """Retrieve not existing set."""
    client = admin.login(client)
    _get_set(client, 9001, headers, 404).json


def test_update_set(client, admin, minimal_oai_set, headers):
    """Update a set."""
    client = admin.login(client)

    s1 = _create_set(client, minimal_oai_set, headers, 201).json

    update = minimal_oai_set.copy()
    update["name"] = "updated"
    update["description"] = "updated"
    update["search_pattern"] = "updated"
    s1_updated = _update_set(client, s1["id"], update, headers, 200).json

    assert s1_updated["name"] == update["name"]
    assert s1_updated["description"] == update["description"]
    assert s1_updated["search_pattern"] == update["search_pattern"]
    assert s1_updated["id"] == s1["id"]
    assert s1_updated["spec"] == s1["spec"]


def test_update_set_invalid_data(client, admin, minimal_oai_set, headers):
    """Update a set with invalid data.

    Most cases are already handled in test_create_set_invalid_data
    """
    client = admin.login(client)

    s1 = _create_set(client, minimal_oai_set, headers, 201).json
    s = minimal_oai_set.copy()
    # changing spec is not allowed
    s["spec"] = "should raise an error"
    with pytest.raises(OAISetSpecUpdateError):
        _update_set(client, s1["id"], s, headers, 400)

    # trying to set data which is read_only
    s = s1.copy()
    s["id"] = 200
    _update_set(client, s1["id"], s, headers, 400)

    s = s1.copy()
    s["created"] = 200
    _update_set(client, s1["id"], s, headers, 400)

    s = s1.copy()
    s["updated"] = 200
    _update_set(client, s1["id"], s, headers, 400)


def test_delete_set(client, admin, minimal_oai_set, headers):
    """Retrieve a set."""
    client = admin.login(client)

    s1 = _create_set(client, minimal_oai_set, headers, 201).json
    _delete_set(client, s1["id"], headers, 204)
    _get_set(client, s1["id"], headers, 404)


def test_delete_set_not_existing(client, admin, headers):
    """Delete not existing set."""
    client = admin.login(client)
    _delete_set(client, 9001, headers, 404).json


def test_search_sets(client, admin, minimal_oai_set, headers):
    """Search sets."""
    client = admin.login(client)

    created_sets = []

    num_sets = 4
    for i in range(num_sets):
        minimal_oai_set["spec"] = minimal_oai_set["name"] = f"set_{i}"
        s1 = _create_set(client, minimal_oai_set, headers, 201).json
        created_sets.append(s1)

    search = _search_sets(client, {}, headers, 200).json
    assert search["hits"]["total"] == num_sets
    for i in range(num_sets):
        assert search["hits"]["hits"][i]["spec"] == created_sets[i]["spec"]
    assert "next" not in search["links"]
    assert "prev" not in search["links"]

    search = _search_sets(
        client, {"size": "1", "page": "2"}, headers, 200
    ).json
    assert "next" in search["links"]
    assert "prev" in search["links"]

    search = _search_sets(
        client, {"sort_direction": "desc"}, headers, 200
    ).json
    for i in range(num_sets):
        assert (
            search["hits"]["hits"][num_sets - 1 - i]["spec"]
            == created_sets[i]["spec"]
        )


def test_search_metadata_formats(client, admin, headers):
    """Retrieve metadata formats."""
    client = admin.login(client)

    available_formats = current_app.config.get(
        "OAISERVER_METADATA_FORMATS", {}
    )
    search = _search_formats(client, headers, 200).json
    assert search["hits"]["total"] == len(available_formats)
    for hit in search["hits"]["hits"]:
        assert hit["id"] in available_formats
        assert hit["schema"] == available_formats[hit["id"]]["schema"]
        assert hit["namespace"] == available_formats[hit["id"]]["namespace"]
