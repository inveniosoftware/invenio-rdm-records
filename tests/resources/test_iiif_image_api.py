# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from io import BytesIO

from PIL import Image
from werkzeug.utils import secure_filename

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


def test_iiif_base(
    running_app, es_clear, client_with_login, headers, minimal_record
):
    client = client_with_login
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers
    )
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 301
    assert (
        response.json["location"]
        ==
        f"https://127.0.0.1:5000/api/iiif/record:{recid}:{file_id}/info.json"
    )


def test_iiif_info(
    running_app, es_clear, client_with_login, headers, minimal_record
):
    client = client_with_login
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers
    )
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 200
    assert response.json == {
        "@context": "http://iiif.io/api/image/2/context.json",
        'profile': ['http://iiif.io/api/image/2/level2.json'],
        'protocol': 'http://iiif.io/api/image',
        "@id":
        f"https://127.0.0.1:5000/api/iiif/record:{recid}:{file_id}",
        "tiles": [{"width": 256, "scaleFactors": [1, 2, 4, 8, 16, 32, 64]}],
        "width": 1280,
        "height": 1024,
    }


def test_api_info_not_found(running_app, es_clear, client):
    response = client.get(f"/iiif/record:1234-abcd:notfound.png/info.json")
    assert response.status_code == 404


def test_iiif_base_restricted_files(
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
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 403

    # Log in user and try again
    login_user(client, users[0])
    response = client.get(f"/iiif/record:{recid}:{file_id}")
    assert response.status_code == 301


def test_iiif_info_restricted_files(
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
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 403

    # Log in user and try again
    login_user(client, users[0])
    response = client.get(f"/iiif/record:{recid}:{file_id}/info.json")
    assert response.status_code == 200


def test_iiif_image_api(
    running_app, es_clear, client_with_login, headers, minimal_record
):
    client = client_with_login
    file_id = "test_image.png"
    recid = publish_record_with_images(
        client, file_id, minimal_record, headers
    )

    # create a new image equal to the one in the record
    tmp_file = BytesIO()
    image = Image.new("RGBA", (1280, 1024), (255, 0, 0, 0))
    image.save(tmp_file, "png")
    tmp_file.seek(0)

    response = client.get(
        f"/iiif/record:{recid}:{file_id}/full/full/0/default.png"
    )
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
        assert (
            response.headers["Content-Disposition"]
            == f"attachment; filename={name}"
        )
