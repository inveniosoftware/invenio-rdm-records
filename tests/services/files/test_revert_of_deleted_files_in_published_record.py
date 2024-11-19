# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test some permissions on RDMRecordFilesResource.

Not every case is tested, but enough high-level ones for it to be useful.
"""

from io import BytesIO

from invenio_rdm_records.proxies import current_rdm_records_service


def attach_file(service, user, recid, key):
    """Attach a file to a record."""
    service.draft_files.init_files(user, recid, data=[{"key": key}])
    service.draft_files.set_file_content(user, recid, key, BytesIO(b"test file"))
    service.draft_files.commit_file(user, recid, key)


def test_revert_of_deleted_files_in_published_record(
    minimal_record, identity_simple, app_with_allowed_edits
):
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    # Create
    draft = service.create(identity_simple, data)

    # Add a file
    attach_file(service, identity_simple, draft.id, "test.pdf")

    # Publish
    record = service.publish(identity_simple, draft.id)

    # Put in edit mode so that draft exists
    draft = service.edit(identity_simple, record.id)

    # Add a new file
    attach_file(service, identity_simple, draft.id, "test2.pdf")
    files = service.draft_files.list_files(identity_simple, draft.id)
    files_keys = [f["key"] for f in files.to_dict()["entries"]]
    assert "test.pdf" in files_keys
    assert "test2.pdf" in files_keys

    record = service.publish(identity_simple, draft.id)

    files = service.files.list_files(identity_simple, record.id)
    files_keys = [f["key"] for f in files.to_dict()["entries"]]
    assert "test.pdf" in files_keys
    assert "test2.pdf" in files_keys

    # Put in edit mode so that draft exists
    draft = service.edit(identity_simple, record.id)

    # delete one file
    service.draft_files.delete_file(identity_simple, draft.id, "test.pdf")
    # publish draft
    record = service.publish(identity_simple, draft.id)
    files = service.files.list_files(identity_simple, record.id)
    files_keys = [f["key"] for f in files.to_dict()["entries"]]

    assert "test2.pdf" in files_keys
    assert len(files_keys) == 1

    # list all files
    file_service_config = service.files.config
    file_cls = file_service_config.record_cls.files.file_cls
    all_files = {
        f.key: f
        for f in file_cls.list_by_record(
            str(record._record.id),
            with_deleted=True,
        )
    }
    deleted_file = all_files["test.pdf"]

    # revert deleted file
    deleted_file.revert(deleted_file.revision_id - 1)

    files = service.files.list_files(identity_simple, record.id)
    files_keys = [f["key"] for f in files.to_dict()["entries"]]

    assert "test.pdf" in files_keys
    assert "test2.pdf" in files_keys
    assert len(files_keys) == 2
