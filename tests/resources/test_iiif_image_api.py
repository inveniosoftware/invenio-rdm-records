# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from io import BytesIO
from urllib.parse import quote

import dictdiffer
from PIL import Image
from werkzeug.utils import secure_filename


def publish_record_with_images(
    client, file_id, record, headers, restricted_files=False
):
    """A record with files."""
    record["files"]["enabled"] = True

    if restricted_files:
        record["access"]["files"] = "restricted"

    # Create a draft
    res = client.post("/records", headers=headers, json=record)
    id_ = res.json["id"]

    # create a new image
    res = client.post(
        f"/records/{id_}/draft/files", headers=headers, json=[{"key": file_id}]
    )
    links = res.json["entries"][0]["links"]
    # Upload a file
    image_file = BytesIO()
    image = Image.new("RGBA", (1280, 1024), (255, 0, 0, 0))
    image.save(image_file, "png")
    image_file.seek(0)
    res1 = client.put(
        links["content"].split("/api", 1)[
            -1
        ],  # Removes the base URL and keeps only the API path
        headers={"content-type": "application/octet-stream"},
        data=image_file,
    )

    # Commit the file
    res2 = client.post(
        links["commit"].split("/api", 1)[
            -1
        ],  # Removes the base URL and keeps only the API path
        headers=headers,
    )

    # Publish the record
    res3 = client.post(f"/records/{id_}/draft/actions/publish", headers=headers)

    return id_


def test_file_links_depending_on_file_extensions(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_id = "test_image.zip"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)
    response = client.get(f"/records/{recid}/files/{file_id}")
    assert "iiif_canvas" not in response.json["links"]
    assert "iiif_base" not in response.json["links"]
    assert "iiif_info" not in response.json["links"]
    assert "iiif_api" not in response.json["links"]

    file_id = "test_image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)
    response = client.get(f"/records/{recid}/files/{file_id}")
    assert "iiif_canvas" in response.json["links"]
    assert "iiif_base" in response.json["links"]
    assert "iiif_info" in response.json["links"]
    assert "iiif_api" in response.json["links"]

    ## Testing with filename with a slash ##

    file_id = "test/image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)
    response = client.get(f"/records/{recid}/files/{file_id}")
    assert "iiif_canvas" in response.json["links"]
    assert "iiif_base" in response.json["links"]
    assert "iiif_info" in response.json["links"]
    assert "iiif_api" in response.json["links"]


def test_iiif_base(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_id = "test_image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 301
    assert (
        response.json["location"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}:{file_id}/info.json"
    )

    ## Testing with filename with a slash and a "#" ##

    file_id = "test/#image.png"
    encoded_file_id = "test%2F%23image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)

    response = client.get(f"/iiif/record:{recid}:{encoded_file_id}")

    assert response.status_code == 301
    assert (
        response.json["location"]
        == f"https://127.0.0.1:5000/api/iiif/record:{recid}:{encoded_file_id}/info.json"
    )


def test_iiif_info(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_id = "test_image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 200
    assert not list(
        dictdiffer.diff(
            response.json,
            {
                "@context": "http://iiif.io/api/image/2/context.json",
                "profile": ["http://iiif.io/api/image/2/level2.json"],
                "protocol": "http://iiif.io/api/image",
                "@id": f"https://127.0.0.1:5000/api/iiif/record:{recid}:{file_id}",
                "tiles": [{"width": 256, "scaleFactors": [1, 2, 4, 8, 16, 32, 64]}],
                "width": 1280,
                "height": 1024,
            },
        )
    )

    ## Testing with filename with a slash and a "#" ##

    file_id = "test/#image.png"
    encoded_file_id = "test%2F%23image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)
    response = client.get(f"/iiif/record:{recid}:{encoded_file_id}/info.json")
    assert response.status_code == 200
    assert response.json == {
        "@context": "http://iiif.io/api/image/2/context.json",
        "profile": ["http://iiif.io/api/image/2/level2.json"],
        "protocol": "http://iiif.io/api/image",
        "@id": f"https://127.0.0.1:5000/api/iiif/record:{recid}:{encoded_file_id}",
        "tiles": [{"width": 256, "scaleFactors": [1, 2, 4, 8, 16, 32, 64]}],
        "width": 1280,
        "height": 1024,
    }


def test_api_info_not_found(running_app, search_clear, client):
    response = client.get(f"/iiif/record:1234-abcd:notfound.png/info.json")
    assert response.status_code == 404


def test_iiif_base_restricted_files(
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
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 403

    # Log in user and try again
    client = uploader.login(client)
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 301

    ## Testing with filename with a slash ##

    file_id = "test/image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers, restricted_files=True
    )
    client = uploader.logout(client)
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 403

    # Log in user and try again
    client = uploader.login(client)
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 301


def test_iiif_info_restricted_files(
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
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 403

    # Log in user and try again
    client = uploader.login(client)
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 200

    ## Testing with filename with a slash ##
    file_id = "test/image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers, restricted_files=True
    )
    client = uploader.logout(client)
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 403

    # Log in user and try again
    client = uploader.login(client)
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 200


def test_iiif_image_api(
    running_app, search_clear, client, uploader, headers, minimal_record
):
    client = uploader.login(client)
    file_id = "test_image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)

    # create a new image equal to the one in the record
    tmp_file = BytesIO()
    image = Image.new("RGBA", (1280, 1024), (255, 0, 0, 0))
    image.save(tmp_file, "png")
    tmp_file.seek(0)

    response = client.get(f"/iiif/record:{recid}:{file_id}/full/full/0/default.png")
    assert response.status_code == 200
    assert response.data == tmp_file.getvalue()

    response = client.get(
        f"/iiif/record:{recid}:{file_id}/200,200,200,200/300,300/!50/color.pdf"
    )
    assert response.status_code == 200

    default_name = secure_filename(
        f"record:{recid}:{file_id}-200200200200-300300-color-50.pdf"
    )
    for dl, name in (
        ("", default_name),
        ("1", default_name),
        ("foo.pdf", "foo.pdf"),
    ):
        response = client.get(
            f"/iiif/record:{recid}:{file_id}/"
            f"200,200,200,200/300,300/!50/color.pdf?dl={dl}"
        )
        assert response.status_code == 200
        assert response.headers["Content-Disposition"] == f"attachment; filename={name}"

    ## Testing with filename with a slash ##
    file_id = "test/image.png"
    recid = publish_record_with_images(client, file_id, minimal_record, headers)

    response = client.get(f"/iiif/record:{recid}:{file_id}/full/full/0/default.png")
    assert response.status_code == 200
    assert response.data == tmp_file.getvalue()

    response = client.get(
        f"/iiif/record:{recid}:{file_id}/200,200,200,200/300,300/!50/color.pdf"
    )
    assert response.status_code == 200

    default_name = secure_filename(
        f"record:{recid}:{file_id}-200200200200-300300-color-50.pdf"
    )
    for dl, name in (
        ("", default_name),
        ("1", default_name),
        ("foo.pdf", "foo.pdf"),
    ):
        response = client.get(
            f"/iiif/record:{recid}:{file_id}/"
            f"200,200,200,200/300,300/!50/color.pdf?dl={dl}"
        )
        assert response.status_code == 200
        assert response.headers["Content-Disposition"] == f"attachment; filename={name}"
