# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the file-download stats event builder."""

from types import SimpleNamespace

import pytest

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.resources.stats.event_builders import (
    file_download_event_builder,
)


@pytest.fixture
def record(minimal_record, parent):
    """A real RDMRecord with a parent."""
    return RDMRecord.create(minimal_record, parent=parent)


@pytest.fixture
def obj():
    """ObjectVersion-shaped data for the file the event is about."""
    return SimpleNamespace(
        bucket_id="bucket-1",
        file_id="file-1",
        key="foo.pdf",
        file=SimpleNamespace(size=1024),
    )


def _preview_url(record, key="foo.pdf", host="127.0.0.1:5000", scheme="https"):
    return f"{scheme}://{host}/records/{record['id']}/preview/{key}"


def _build(app, record, obj, referrer, exclude_preview_events):
    """Run the builder under a request context with the given referrer."""
    app.config["RDM_STATS_EXCLUDE_PREVIEW_FILE_DOWNLOAD_EVENTS"] = (
        exclude_preview_events
    )
    headers = [("Referer", referrer)] if referrer else []
    with app.test_request_context("/", headers=headers):
        return file_download_event_builder({}, app, record=record, obj=obj)


@pytest.mark.parametrize(
    "exclude_preview_events, referrer_kind, expected_drop",
    [
        # Flag off → preview Referer ignored, event always built.
        (False, "same_file_preview", False),
        # Flag on
        (True, "none", False),
        (True, "same_file_preview", True),
        (True, "same_file_preview_with_query", True),
        (True, "other_file_preview", False),
        (True, "landing_page", False),
        (True, "cross_origin_preview", False),
    ],
)
def test_preview_referrer_filtering(
    app, record, obj, exclude_preview_events, referrer_kind, expected_drop
):
    """The builder drops events whose Referer is the file's own preview page."""
    referrers = {
        "none": None,
        "same_file_preview": _preview_url(record),
        "same_file_preview_with_query": _preview_url(record) + "?preview=0#section",
        "other_file_preview": _preview_url(record, key="other.pdf"),
        "landing_page": f"https://127.0.0.1:5000/records/{record['id']}",
        "cross_origin_preview": _preview_url(record, host="attacker.example"),
    }
    referrer = referrers[referrer_kind]

    event = _build(
        app, record, obj, referrer, exclude_preview_events=exclude_preview_events
    )

    if expected_drop:
        assert event is None
    else:
        assert event is not None
        assert event["recid"] == record["id"]
        assert event["file_key"] == "foo.pdf"
        assert event["referrer"] == referrer
