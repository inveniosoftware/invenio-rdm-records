# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test errors."""


# Helpers


def save_partial_draft(client, partial_record, headers):
    """Save a partially filled record."""
    response = client.post("/records", json=partial_record, headers=headers)
    assert response.status_code == 201
    return response


# Tests


def test_simple_field_error(
        client_with_login, minimal_record, running_app, es_clear, headers
):
    client = client_with_login
    minimal_record["metadata"]["publication_date"] = ""
    response = save_partial_draft(client, minimal_record, headers)
    recid = response.json['id']

    response = client.post(
        f"/records/{recid}/draft/actions/publish",
        headers=headers
    )

    assert 400 == response.status_code
    expected = [
        {
            "field": "metadata.publication_date",
            "messages": ["Missing data for required field."]
        },
    ]
    assert expected == response.json["errors"]


def test_nested_field_error(
        client_with_login, minimal_record, running_app, es_clear, headers
):
    client = client_with_login
    minimal_record["metadata"]["creators"] = [
        {
            "person_or_org": {
                "name": "Julio Cesar",
                "type": "personal",
                "given_name": "Julio",
                "family_name": "Cesar",
            }
        },
        # No name even though it is required
        {
            "person_or_org": {
                "type": "organizational",
            }
        }
    ]
    response = save_partial_draft(client, minimal_record, headers)
    recid = response.json['id']

    response = client.post(
        f"/records/{recid}/draft/actions/publish",
        headers=headers
    )

    assert 400 == response.status_code
    expected = [
        {
            "field": "metadata.creators.1.person_or_org.name",
            "messages": ["Name cannot be blank."]
        }
    ]
    assert expected == response.json["errors"]


def test_multiple_errors(
    client_with_login, minimal_record, running_app, es_clear, headers
):
    client = client_with_login
    minimal_record["metadata"]["publication_date"] = ""
    minimal_record["metadata"]["additional_titles"] = [{
        "title": "A Romans story",
        "type": "invalid",
        "lang": {
            "id": "eng"
        }
    }]
    response = save_partial_draft(client, minimal_record, headers)
    recid = response.json['id']

    response = client.post(
        f"/records/{recid}/draft/actions/publish",
        headers=headers
    )

    assert 400 == response.status_code
    errors = response.json["errors"]
    expected_errors = [
        {
            "field": "metadata.publication_date",
            "messages": ["Missing data for required field."]
        },
        {
            "field": "metadata.additional_titles.0.type",
            "messages": [
                "Invalid value. Choose one of ['alternativetitle', "
                "'other', 'subtitle', 'translatedtitle']."
            ]
        }
    ]
    assert len(expected_errors) == len(errors)
    assert all([e in errors for e in expected_errors])
