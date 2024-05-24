# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Signposting resource tests."""


def test_link_in_metadata_resource_response_headers(
    running_app, client_with_login, minimal_record, publish_record
):
    """Check content-negotiated API response contains API link."""
    record_json = publish_record(client_with_login, minimal_record)
    record_id = record_json["id"]

    response = client_with_login.head(
        f"/records/{record_id}", headers={"accept": "application/marcxml+xml"}
    )

    assert (
        response.headers["Link"]
        == f'<https://127.0.0.1:5000/api/records/{record_id}> ; rel="linkset" ; type="application/linkset+json"'  # noqa
    )


# Just a sanity check
def test_signposting_link_permissions(
    client, client_with_login, minimal_restricted_record, publish_record
):
    record_json = publish_record(client_with_login, minimal_restricted_record)
    record_id = record_json["id"]
    response = client_with_login.head(
        f"/records/{record_id}", headers={"accept": "application/marcxml+xml"}
    )
    link = response.headers["Link"]

    response = client.get(link, headers={"accept-type": "application/linkset+json"})

    assert 404 == response.status_code


def test_linkset_endpoint(
    running_app, client_with_login, minimal_record, publish_record
):
    record_json = publish_record(client_with_login, minimal_record)
    record_id = record_json["id"]

    response = client_with_login.get(
        f"/records/{record_id}", headers={"accept": "application/linkset+json"}
    )

    assert 200 == response.status_code
    assert "application/linkset+json" == response.headers["content-type"]
