# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the handlers."""

from io import BytesIO

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.resources.iiif import image_opener


def _publish_record_with_file(file_id, file_content, identity, record):
    # client_with_login will push the identity to g
    # enable files on record
    record["files"]["enabled"] = True
    # create a record with a file
    service = current_rdm_records.records_service
    draft = service.create(identity, record)
    # add files

    service.draft_files.init_files(
        draft.id, identity, data=[{'key': file_id}])
    service.draft_files.set_file_content(
        draft.id, file_id, identity, BytesIO(file_content)
    )
    service.draft_files.commit_file(draft.id, file_id, identity)
    # publish the record
    record = service.publish(draft.id, identity)

    return record.id


def test_image_opener(
    running_app, es_clear, client_with_login, identity_simple, minimal_record
):
    file_id = "test_file"
    file_content = b'test file content'
    recid = _publish_record_with_file(
        file_id, file_content, identity_simple, minimal_record)

    key = f"{recid}:{file_id}"
    fp = image_opener(key)
    data = fp.read()
    assert data == file_content
    fp.close()


def test_image_opener_not_found(
    running_app, es_clear, client_with_login, identity_simple, minimal_record
):
    file_id = "test_file"
    file_content = b'test file content'
    recid = _publish_record_with_file(
        file_id, file_content, identity_simple, minimal_record)

    key = f"{recid}:different"
    fp = image_opener(key)
    assert not fp
