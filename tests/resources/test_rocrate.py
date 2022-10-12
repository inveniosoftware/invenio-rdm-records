# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RO-Crate resource tests."""

import pytest


@pytest.fixture
def headers(headers):
    """RO-Crate Content-Type headers."""
    return {
        **headers,
        "content-type": 'application/ld+json;profile="https://w3id.org/ro/crate/1.1"',
    }


def test_rocrate_content_type(running_app, client_with_login, headers, search_clear):
    """Test draft creation via RO-Crate metadata payload."""
    client = client_with_login
    response = client.post(
        "/records",
        json={
            "@context": [
                "https://w3id.org/ro/crate/1.0/context",
                {"@vocab": "https://schema.org/"},
            ],
            "@graph": [
                {
                    "@id": "ro-crate-metadata.json",
                    "@type": "CreativeWork",
                    "about": {"@id": "./"},
                    "identifier": "ro-crate-metadata.json",
                    "conformsTo": {"@id": "https://w3id.org/ro/crate/1.0"},
                },
                {
                    "@id": "./",
                    "@type": "Dataset",
                    "name": "Test dataset",
                    "description": ["This is a test dataset."],
                    "license": [{"@id": "#f96b4aaf-7cdc-4d21-9c13-d26546d50fd4"}],
                    "datePublished": ["2022-10-12T22:00:00.000Z"],
                    "author": [
                        {"@id": "#98ccae13-bb8a-41e5-9bac-1db0652100d5"},
                        {"@id": "#575492d0-8743-410c-bb79-25b4bb9de9d3"},
                    ],
                    "keywords": ["machine learning", "nlp"],
                },
                {
                    "@id": "#f96b4aaf-7cdc-4d21-9c13-d26546d50fd4",
                    "@type": "CreativeWork",
                    "name": "MIT",
                    "description": ["MIT License"],
                },
                {
                    "@id": "#98ccae13-bb8a-41e5-9bac-1db0652100d5",
                    "@type": "Person",
                    "familyName": ["Smith"],
                    "givenName": ["John"],
                    "affiliation": [
                        {"@id": "https://ror.org/01ggx4157"},
                    ],
                },
                {
                    "@id": "#575492d0-8743-410c-bb79-25b4bb9de9d3",
                    "@type": "Organization",
                    "name": "Research Org",
                },
                {
                    "@id": "https://ror.org/01ggx4157",
                    "@type": "Organization",
                    "name": "European Organization for Nuclear Research",
                },
            ],
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json["metadata"] == {
        "title": "Test dataset",
        "description": "This is a test dataset.",
        "publication_date": "2022-10-12",
        "resource_type": {"id": "dataset", "title": {"en": "Dataset"}},
        "creators": [
            {
                "affiliations": [
                    {"name": "European Organization for Nuclear Research"}
                ],
                "person_or_org": {
                    "family_name": "Smith",
                    "given_name": "John",
                    "name": "Smith, John",
                    "type": "personal",
                },
            },
            {
                "person_or_org": {
                    "name": "Research Org",
                    "type": "organizational",
                },
            },
        ],
        "rights": [{"description": {"en": "MIT License"}, "title": {"en": "MIT"}}],
        "subjects": [{"subject": "machine learning"}, {"subject": "nlp"}],
    }


def test_invalid_rocrate(running_app, client_with_login, headers, search_clear):
    """Test invalid RO-Crate metadata payload."""
    client = client_with_login

    # Check missing "@graph"
    response = client.post("/records", json={}, headers=headers)
    assert response.status_code == 400
    assert response.json == {
        "message": "Invalid RO-Crate metadata format, missing '@graph' key.",
        "status": 400,
    }

    # Check required fields
    response = client.post(
        "/records",
        json={
            "@context": [
                "https://w3id.org/ro/crate/1.0/context",
                {"@vocab": "https://schema.org/"},
            ],
            "@graph": [
                {
                    "@id": "ro-crate-metadata.json",
                    "@type": "CreativeWork",
                    "about": {"@id": "./"},
                    "identifier": "ro-crate-metadata.json",
                    "conformsTo": {"@id": "https://w3id.org/ro/crate/1.0"},
                },
                {
                    "@id": "./",
                    "@type": "Dataset",
                },
            ],
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert {(e["field"], e["messages"][0]) for e in response.json["errors"]} == {
        ("license", "Missing data for required field."),
        ("name", "Missing data for required field."),
        ("datePublished", "Missing data for required field."),
        ("author", "Missing data for required field."),
    }

    # Check required fields
    response = client.post(
        "/records",
        json={
            "@context": [
                "https://w3id.org/ro/crate/1.0/context",
                {"@vocab": "https://schema.org/"},
            ],
            "@graph": [
                {
                    "@id": "ro-crate-metadata.json",
                    "@type": "CreativeWork",
                    "about": {"@id": "./"},
                    "identifier": "ro-crate-metadata.json",
                    "conformsTo": {"@id": "https://w3id.org/ro/crate/1.0"},
                },
                {
                    "@id": "./",
                    "@type": "Dataset",
                    "name": "Test dataset",
                    "license": [{"@id": "#f96b4aaf-7cdc-4d21-9c13-d26546d50fd4"}],
                    "datePublished": ["2022-10-12T22:00:00.000Z"],
                    "author": [
                        {"@id": "#98ccae13-bb8a-41e5-9bac-1db0652100d5"},
                        {"@id": "#575492d0-8743-410c-bb79-25b4bb9de9d3"},
                        {"@id": "#41f1b05c-aad9-42f2-8d35-13495e7452d2"},
                    ],
                },
                {
                    "@id": "#f96b4aaf-7cdc-4d21-9c13-d26546d50fd4",
                    "@type": "CreativeWork",
                },
                {
                    "@id": "#98ccae13-bb8a-41e5-9bac-1db0652100d5",
                    "@type": "Person",
                    "affiliation": [
                        {"@id": "https://ror.org/01ggx4157"},
                    ],
                },
                {
                    "@id": "#575492d0-8743-410c-bb79-25b4bb9de9d3",
                    "@type": "Organization",
                },
                {
                    "@id": "https://ror.org/01ggx4157",
                    "@type": "Organization",
                },
                {
                    "@id": "#41f1b05c-aad9-42f2-8d35-13495e7452d2",
                    "@type": "invalid",
                },
            ],
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert {(e["field"], e["messages"][0]) for e in response.json["errors"]} == {
        ("author.0.familyName", "Missing data for required field."),
        ("author.0.givenName", "Missing data for required field."),
        ("author.0.affiliation.0.name", "Missing data for required field."),
        ("author.1.name", "Missing data for required field."),
        ("author.2.@type", "'@type' must be 'Person' or 'Organization'"),
        ("license.name", "Missing data for required field."),
    }
