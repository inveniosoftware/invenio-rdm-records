from pathlib import Path

from invenio_rdm_records.proxies import current_rdm_records_service


def publish_record_with_pdf(client, file_key, record, headers):
    """A record with files."""
    record["files"]["enabled"] = True

    # Create a draft
    res = client.post("/records", headers=headers, json=record)
    recid = res.json["id"]

    # create a new image
    res = client.post(
        f"/records/{recid}/draft/files", headers=headers, json=[{"key": file_key}]
    )

    # create a new image
    res = client.post(
        f"/records/{recid}/draft/files", headers=headers, json=[{"key": file_key}]
    )

    # Upload a file
    with (Path(__file__).parent / "loremipsum.pdf").open("rb") as fd:
        res = client.put(
            f"/records/{recid}/draft/files/{file_key}/content",
            headers={"content-type": "application/octet-stream"},
            data=fd,
        )

    # Commit the file
    res = client.post(
        f"/records/{recid}/draft/files/{file_key}/commit", headers=headers
    )

    # Publish the record
    res = client.post(f"/records/{recid}/draft/actions/publish", headers=headers)

    return recid


def test_pdf_text_extraction(running_app, client, uploader, headers, minimal_record):
    client = uploader.login(client)
    file_key = "loremipdum.pdf"
    recid = publish_record_with_pdf(client, file_key, minimal_record, headers)

    response = client.get(f"/records/{recid}")
    assert response.status_code == 200

    data = response.json
    assert "media_files" in data
    assert data["media_files"]["enabled"]
    assert data["media_files"]["count"] == 1
    assert "loremipdum.pdf.txt" in data["media_files"]["entries"]

    # Check file content
    record = current_rdm_records_service.record_cls.pid.resolve(recid)
    full_text_file = record.media_files[f"{file_key}.txt"]
    with full_text_file.open_stream("rb") as f:
        data = f.read().decode()

    assert "Test" in data
