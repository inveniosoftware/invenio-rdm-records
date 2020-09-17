# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test errors."""

import pytest

HEADERS = {"content-type": "application/json", "accept": "application/json"}


# TODO: remove es_clear: none of the below should index anything
def test_simple_field_error(client, minimal_input_record, es_clear):
    minimal_input_record["metadata"]["publication_date"] = ""

    response = client.post(
        "/records", json=minimal_input_record, headers=HEADERS
    )

    assert response.status_code == 400
    assert response.json["status"] == 400
    assert response.json["message"] == "A validation error occurred."
    errors = response.json["errors"]
    expected_errors = [
        {
            "field": "metadata.publication_date",
            "messages": ["Please provide a valid date or interval."],
        }
    ]
    assert expected_errors == errors


def test_nested_field_error(client, minimal_input_record, es_clear):
    minimal_input_record["metadata"]["creators"] = [
        {
            "name": "Julio Cesar",
            "type": "Personal",
            "given_name": "Julio",
            "family_name": "Cesar",
        },
        # Invalid ror identifier
        {
            "name": "California Digital Library",
            "type": "Organizational",
            "identifiers": {
                "ror": "9999-9999-9999-9999",
            }
        }
    ]

    response = client.post(
        "/records", json=minimal_input_record, headers=HEADERS
    )

    assert response.status_code == 400
    errors = response.json["errors"]
    expected_errors = [
        {
            # Could be more specific...
            "field": "metadata.creators.1.identifiers",
            "messages": ["Invalid identifier."]
        }
    ]
    assert expected_errors == errors


@pytest.mark.skip()
def test_multiple_errors(client, minimal_input_record):
    minimal_input_record["metadata"]["publication_date"] = ""
    minimal_input_record["metadata"]["titles"] = [{
        "title": "A Romans story",
        "type": "invalid",
        "lang": "eng"
    }]

    response = client.post(
        "/records", json=minimal_input_record, headers=HEADERS
    )

    assert response.status_code == 400
    errors = response.json["errors"]
    expected_errors = [
        {
            "field": "metadata.publication_date",
            "messages": ["Please provide a valid date or interval."]
        },
        {
            "field": "metadata.titles.0.type",  # TODO: This is the failing one
            "messages": [
                "Invalid title type. Choose one of ['AlternativeTitle', "
                "'MainTitle', 'Other', 'Subtitle', 'TranslatedTitle']."
            ]
        }
    ]
    assert len(expected_errors) == len(errors)
    assert all([e in errors for e in expected_errors])
