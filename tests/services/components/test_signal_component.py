# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test signal component."""

from io import BytesIO
from zipfile import ZipFile

import pytest

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.components import DefaultRecordsComponents
from invenio_rdm_records.services.components.signal import SignalComponent
from invenio_rdm_records.services.signals import post_publish_signal


@pytest.fixture()
def service(running_app):
    """The record service."""
    return current_rdm_records.records_service


@pytest.fixture(scope="module")
def zip_file():
    """Github repository ZIP fixture."""
    memfile = BytesIO()
    zipfile = ZipFile(memfile, "w")
    zipfile.writestr("test.txt", "hello world")
    zipfile.close()
    memfile.seek(0)
    return memfile


def add_file_to_draft(identity, draft_id, file_name, file_contents):
    """Add a file to the record."""
    draft_file_service = current_rdm_records.records_service.draft_files

    draft_file_service.init_files(identity, draft_id, data=[{"key": file_name}])
    draft_file_service.set_file_content(identity, draft_id, file_name, file_contents)
    result = draft_file_service.commit_file(identity, draft_id, file_name)
    return result


def test_publish_signal_fired(
    running_app, service, minimal_record, identity_simple, monkeypatch, zip_file
):
    """Test that the signal is fired."""
    sentinel = {"called": False}

    def _signal_sent(sender, **kwargs):
        sentinel["called"] = True

    default_cmps = running_app.app.config.get(
        "RDM_RECORDS_SERVICE_COMPONENTS", DefaultRecordsComponents
    )
    monkeypatch.setitem(
        running_app.app.config,
        "RDM_RECORDS_SERVICE_COMPONENTS",
        default_cmps + [SignalComponent],
    )
    minimal_record["files"]["enabled"] = True

    # Create
    draft = service.create(identity_simple, minimal_record)
    add_file_to_draft(identity_simple, draft.id, "test.zip", zip_file)

    with post_publish_signal.connected_to(_signal_sent):
        # Publish
        assert sentinel["called"] == False
        record = service.publish(identity_simple, draft.id)
        assert sentinel["called"] == True
