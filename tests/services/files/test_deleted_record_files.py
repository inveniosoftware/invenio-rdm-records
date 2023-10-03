# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test some permissions on deleted record files."""

from io import BytesIO

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.errors import RecordDeletedException


def attach_file(service, user, recid, key):
    """Attach a file to a record."""
    service.draft_files.init_files(user, recid, data=[{"key": key}])
    service.draft_files.set_file_content(user, recid, key, BytesIO(b"test file"))
    service.draft_files.commit_file(user, recid, key)


def test_deleted_records_file_flow(
    location, minimal_record, identity_simple, superuser_identity, running_app
):
    """Test the lifecycle of a deleted record file ."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Add a file
    attach_file(service, identity_simple, draft.id, "test.pdf")

    # Publish
    record = service.publish(identity_simple, draft.id)
    recid = record["id"]

    # Delete record
    service.delete_record(superuser_identity, record["id"], {})

    # List files
    with pytest.raises(RecordDeletedException):
        file_service.list_files(identity_simple, recid)

    result = file_service.list_files(superuser_identity, recid)
    assert result.to_dict()["entries"][0]["key"] == "test.pdf"
    assert result.to_dict()["entries"][0]["storage_class"] == "L"

    # Read file metadata
    with pytest.raises(RecordDeletedException):
        file_service.read_file_metadata(identity_simple, recid, "test.pdf")

    result = file_service.read_file_metadata(superuser_identity, recid, "test.pdf")
    assert result.to_dict()["key"] == "test.pdf"
    assert result.to_dict()["storage_class"] == "L"

    # Retrieve file
    with pytest.raises(RecordDeletedException):
        file_service.get_file_content(identity_simple, recid, "test.pdf")

    result = file_service.get_file_content(superuser_identity, recid, "test.pdf")
    assert result.file_id == "test.pdf"

    # Delete file
    with pytest.raises(PermissionDeniedError):
        file_service.delete_file(identity_simple, recid, "test.pdf")

    recid = record["id"]
    file_to_initialise = [
        {
            "key": "article.txt",
            "checksum": "md5:c785060c866796cc2a1708c997154c8e",
            "size": 17,  # 2kB
            "metadata": {
                "description": "Published article PDF.",
            },
        }
    ]

    # Initialize file saving
    with pytest.raises(PermissionDeniedError):
        file_service.init_files(identity_simple, recid, file_to_initialise)

    # Update file content
    with pytest.raises(PermissionDeniedError):
        content = BytesIO(b"test file content")
        file_service.set_file_content(
            identity_simple,
            recid,
            file_to_initialise[0]["key"],
            content,
            content.getbuffer().nbytes,
        )

    # Commit file
    with pytest.raises(PermissionDeniedError):
        file_service.commit_file(identity_simple, recid, "article.txt")
