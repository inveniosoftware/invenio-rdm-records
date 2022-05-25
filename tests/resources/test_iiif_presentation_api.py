# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the handlers."""

from io import BytesIO

from PIL import Image
from tripoli import IIIFValidator

from tests.helpers import login_user, logout_user


def publish_record_with_images(
    client, file_id, record, headers, restricted_files=False
):
    """A record with files."""
    record["files"]["enabled"] = True
    if restricted_files:
        record["access"]["files"] = "restricted"

    # Create a draft
    res = client.post("/records", headers=headers, json=record)
    id_ = res.json['id']

    # create a new image
    res = client.post(f"/records/{id_}/draft/files", headers=headers, json=[
        {'key': file_id}
    ])

    # Upload a file
    image_file = BytesIO()
    image = Image.new("RGBA", (1280, 1024), (255, 0, 0, 0))
    image.save(image_file, "png")
    image_file.seek(0)
    res = client.put(
        f"/records/{id_}/draft/files/{file_id}/content",
        headers={'content-type': 'application/octet-stream'},
        data=image_file,
    )

    # Commit the file
    res = client.post(
        f"/records/{id_}/draft/files/{file_id}/commit", headers=headers
    )

    # Publish the record
    res = client.post(f"/records/{id_}/draft/actions/publish", headers=headers)

    return id_


def test_iiif_manifest_schema(
    running_app, es_clear, client_with_login, headers, minimal_record
):
    client = client_with_login
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers
    )
    response = client.get(f"/iiif/record:{recid}/manifest")
    manifest = response.json
    validator = IIIFValidator(fail_fast=False)
    validator.validate(manifest)
    assert not validator.errors


def test_iiif_manifest(
    running_app, es_clear, client_with_login, headers, minimal_record
):
    client = client_with_login
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers
    )
    response = client.get(f"/iiif/record:{recid}/manifest")
    assert response.status_code == 200

    manifest = response.json
    assert (
        manifest["@id"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}/manifest"
    )
    assert manifest["label"] == "A Romans story"
    assert "sequences" in manifest
    assert len(manifest["sequences"]) == 1

    sequence = manifest["sequences"][0]
    assert (
        sequence["@id"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}/sequence/default"
    )
    assert "canvases" in sequence
    assert len(sequence["canvases"]) == 1

    canvas = sequence["canvases"][0]
    assert (
        canvas["@id"]
        ==
        f"https://127.0.0.1:5000/api/iiif/record:{recid}/canvas/test_image.png"
    )
    assert canvas["height"] == 1024
    assert canvas["width"] == 1280
    assert "images" in canvas
    assert len(canvas["images"]) == 1

    image = canvas["images"][0]
    assert image["motivation"] == "sc:painting"
    assert image["resource"]["height"] == 1024
    assert image["resource"]["width"] == 1280
    assert (
        image["resource"]["@id"]
        ==
        f"https://127.0.0.1:5000/api/iiif/"
        f"record:{recid}:{file_id}/full/full/0/default.png"
    )
    assert (
        image["resource"]["service"]["@id"]
        ==
        f"https://127.0.0.1:5000/api/iiif/record:{recid}:{file_id}/info.json"
    )


def test_iiif_manifest_restricted_files(
    running_app,
    es_clear,
    client_with_login,
    headers,
    minimal_record,
    users,
):
    client = client_with_login
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers, restricted_files=True
    )
    logout_user(client)
    response = client.get(f"/iiif/record:{recid}/manifest")
    # TODO: should we return only the parts the user has access to?
    assert response.status_code == 403

    # Log in user and try again
    login_user(client, users[0])
    response = client.get(f"/iiif/record:{recid}/manifest")
    assert response.status_code == 200
