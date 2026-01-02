# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""


from invenio_base import invenio_url_for


def test_version():
    """Test version import."""
    from invenio_rdm_records import __version__

    assert __version__


def test_link_generation(running_app):
    """Make sure that UI app can generate UI/API urls.

    The reverse is tested where the API app is loaded (here the UI app is loaded).
    """
    # a UI endpoint
    assert (
        "https://127.0.0.1:5000/records/12345-abcde/files/filename.txt"
        == invenio_url_for(
            "invenio_app_rdm_records.record_file_download",
            pid_value="12345-abcde",
            filename="filename.txt",
        )
    )
    # an API endpoint
    assert "https://127.0.0.1:5000/api/records/12345-abcde" == invenio_url_for(
        "records.read", pid_value="12345-abcde"
    )
