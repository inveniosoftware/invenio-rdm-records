# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the files dumpers."""

from io import BytesIO

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord


def attach_file(service, user, recid, key):
    """Attach a file to a record."""
    service.draft_files.init_files(user, recid, data=[{"key": key}])
    service.draft_files.set_file_content(user, recid, key, BytesIO(b"test file"))
    service.draft_files.commit_file(user, recid, key)


def test_files_dumper(
    running_app, minimal_record, users, identity_simple, anonymous_identity, location
):
    """Test that file dumper.

    Test that the dumper is hinding all files information from record indexing if the
    latter is public with restricted files
    """

    # Create the record
    service = current_rdm_records.records_service
    minimal_record["files"] = {"enabled": True}
    # restrict files
    minimal_record["access"] = {
        "record": "public",
        "files": "restricted",
    }
    draft = service.create(identity_simple, minimal_record)

    # Add a file
    attach_file(service, identity_simple, draft["id"], "test.pdf")

    # Publish the draft
    record = service.publish(id_=draft["id"], identity=identity_simple)
    RDMRecord.index.refresh()

    # Search for files count
    assert (
        service.search(
            identity_simple,
            {"q": "files.count:>0"},
        ).total
        == 0
    )

    # Anonymous
    assert (
        service.search(
            anonymous_identity,
            {"q": "files.count:>0"},
        ).total
        == 0
    )

    # Edit the record to make files public
    draft = service.edit(identity_simple, record["id"]).to_dict()

    # open files
    draft["access"] = {
        "record": "public",
        "files": "public",
    }
    draft = service.update_draft(id_=draft["id"], identity=identity_simple, data=draft)
    record = service.publish(id_=draft["id"], identity=identity_simple)
    RDMRecord.index.refresh()

    # Search for files count
    assert (
        service.search(
            identity_simple,
            {"q": "files.count:>0"},
        ).total
        == 1
    )

    # Anonymous
    assert (
        service.search(
            anonymous_identity,
            {"q": "files.count:>0"},
        ).total
        == 1
    )

    # Edit the record to make files resticted again
    draft = service.edit(identity_simple, record["id"]).to_dict()

    # open files
    draft["access"] = {
        "record": "public",
        "files": "restricted",
    }
    draft = service.update_draft(id_=draft["id"], identity=identity_simple, data=draft)
    record = service.publish(id_=draft["id"], identity=identity_simple)
    RDMRecord.index.refresh()

    # Search for files count
    assert (
        service.search(
            identity_simple,
            {"q": "files.count:>0"},
        ).total
        == 0
    )

    # Anonymous
    assert (
        service.search(
            anonymous_identity,
            {"q": "files.count:>0"},
        ).total
        == 0
    )
