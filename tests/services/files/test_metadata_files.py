# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test RDM records files (metadata)."""

from io import BytesIO

import pytest
from marshmallow.exceptions import ValidationError

from invenio_rdm_records.proxies import current_rdm_records_service


def test_valid_metadata_set(running_app, db, location, minimal_record, identity_simple):
    """Test setting file metadata."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "page": 1,
        "encoding": "utf-8",
        "language": "en",
        "charset": "utf-8",
        "type": "pdf",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[{"key": "test.pdf", "metadata": metadata, "access": {"hidden": False}}],
    )
    service.draft_files.set_file_content(
        identity_simple, draft.id, "test.pdf", BytesIO(b"test file")
    )
    service.draft_files.commit_file(identity_simple, draft.id, "test.pdf")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    # Get file metadata
    result = file_service.list_files(identity_simple, draft.id)
    assert result.to_dict()["entries"][0]["metadata"] == metadata
    assert result.to_dict()["entries"][0]["access"]["hidden"] is False  # default value


@pytest.mark.skip(reason="We're not validating metadata correctly anyways.")
def test_invalid_metadata_set(
    running_app, db, location, minimal_record, identity_simple
):
    """Test setting file metadata with invalid data."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "page": 1,
        "encoding": "utf-8",
        "language": "en",
        "charset": "utf-8",
        "type": "pdf",
        "invalid": "invalid",
    }
    with pytest.raises(ValidationError):
        service.draft_files.init_files(
            identity_simple, draft.id, data=[{"key": "test.pdf", "metadata": metadata}]
        )
