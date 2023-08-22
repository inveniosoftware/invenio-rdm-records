# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2023 Data Futures GmbH.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the handlers."""

import random
from io import BytesIO

import pytest
from PIL import Image
from tripoli import IIIFValidator


def publish_record_with_images(
    client, file_ids, record, headers, restricted_files=False
):
    # generate a random RGBA value tuple
    random_color = lambda: tuple(random.randint(0, 255) for _ in range(4))

    """A record with files."""
    record["files"]["enabled"] = True
    if restricted_files:
        record["access"]["files"] = "restricted"

    # Create a draft
    res = client.post("/records", headers=headers, json=record)
    id_ = res.json["id"]

    for f in file_ids:
        # create a new image
        res = client.post(
            f"/records/{id_}/draft/files", headers=headers, json=[{"key": f}]
        )

        # Upload a file
        image_file = BytesIO()
        image = Image.new("RGBA", (1280, 1024), random_color())
        image.save(image_file, "png")
        image_file.seek(0)
        res = client.put(
            f"/records/{id_}/draft/files/{f}/content",
            headers={"content-type": "application/octet-stream"},
            data=image_file,
        )

        # Commit the file
        res = client.post(f"/records/{id_}/draft/files/{f}/commit", headers=headers)

    # set a default_preview image
    record["files"]["default_preview"] = file_ids[-1]
    res = client.put(f"/records/{id_}/draft", headers=headers, json=record)

    # Publish the record
    res = client.post(f"/records/{id_}/draft/actions/publish", headers=headers)

    return id_


@pytest.mark.skip("to be fixed, bug exposed during fixes in another scope")
def test_iiif_manifest_schema(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_ids = ["test_image_001.png", "test_image_002.png"]
    recid = publish_record_with_images(client, file_ids, minimal_record, headers)
    response = client.get(f"/iiif/record:{recid}/manifest")
    manifest = response.json
    validator = IIIFValidator(fail_fast=False)
    validator.validate(manifest)
    assert not validator.errors


@pytest.mark.skip("to be fixed, bug exposed during fixes in another scope")
def test_iiif_manifest(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_ids = ["test_image_001.png", "test_image_002.png"]
    recid = publish_record_with_images(client, file_ids, minimal_record, headers)
    response = client.get(f"/iiif/record:{recid}/manifest")
    assert response.status_code == 200

    manifest = response.json
    assert manifest["@id"] == f"https://127.0.0.1:5000/api/iiif/record:{recid}/manifest"
    assert manifest["label"] == "A Romans story"
    assert "sequences" in manifest

    sequence = manifest["sequences"][0]
    assert (
        sequence["@id"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}/sequence/default"
    )
    assert (
        sequence["startCanvas"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}/canvas/{file_ids[-1]}"
    )
    assert "canvases" in sequence
    assert len(sequence["canvases"]) == len(file_ids)
    canvas = sequence["canvases"][0]

    assert (
        canvas["@id"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}/canvas/test_image.png"
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
        image["resource"]["@id"] == f"https://127.0.0.1:5000/api/iiif/"
        f"record:{recid}:{file_ids[0]}/full/full/0/default.png"
    )
    assert (
        image["resource"]["service"]["@id"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}:{file_ids[0]}"
    )


def test_empty_iiif_manifest(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_ids = ["test_file.zip"]
    recid = publish_record_with_images(client, file_ids, minimal_record, headers)
    response = client.get(f"/iiif/record:{recid}/manifest")
    assert response.status_code == 200
    manifest = response.json
    assert not manifest["sequences"][0]["canvases"]


@pytest.mark.skip("to be fixed, bug exposed during fixes in another scope")
def test_iiif_manifest_restricted_files(
    running_app,
    search_clear,
    client,
    uploader,
    headers,
    minimal_record,
    users,
):
    client = uploader.login(client)
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers, restricted_files=True
    )
    client = uploader.logout(client)
    response = client.get(f"/iiif/record:{recid}/manifest")
    # TODO: should we return only the parts the user has access to?
    assert response.status_code == 403

    # Log in user and try again
    client = uploader.login(client)
    response = client.get(f"/iiif/record:{recid}/manifest")
    assert response.status_code == 200
