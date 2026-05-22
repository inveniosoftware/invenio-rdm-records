# SPDX-FileCopyrightText: 2023 TU Wien.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Custom event builders for the InvenioRDM statistics.

Note that the arguments to these functions will be the same as passed to the
``EventEmitter`` objects when they are called.
Currently in InvenioRDM this is done in resources (for API) and view functions (for UI).
As such, it is assumed that a request context is available (and thus, Flask's global
``request`` is accessible).
"""

from datetime import datetime, timezone
from urllib.parse import urlsplit

from flask import current_app, request
from invenio_base import invenio_url_for
from invenio_stats.utils import get_user
from werkzeug.routing.exceptions import BuildError

# note: the event builders are located under resources, because they access some
#       information that is usually only available on the resources level (such as
#       request context) and we haven't found a more suitable home for them so far


def _is_file_preview_url(url, recid, filename):
    """Return True if the URL is the preview page URL of this file."""
    if not url:
        return False

    try:
        preview_url = invenio_url_for(
            "invenio_app_rdm_records.record_file_preview",
            pid_value=recid,
            filename=filename,
        )
    except BuildError:
        return False

    url_parts = urlsplit(url)
    preview_parts = urlsplit(preview_url)
    return (
        url_parts.scheme == preview_parts.scheme
        and url_parts.netloc == preview_parts.netloc
        and url_parts.path == preview_parts.path
    )


def file_download_event_builder(event, sender_app, **kwargs):
    """Build a file-download event.

    *Note* that this function assumes a request context by accessing properties of
    Flask's global ``request`` object.
    """
    assert "record" in kwargs
    assert "obj" in kwargs

    record = kwargs["record"]
    obj = kwargs["obj"]
    exclude_preview_events = current_app.config.get(
        "RDM_STATS_EXCLUDE_PREVIEW_FILE_DOWNLOAD_EVENTS", False
    )
    if exclude_preview_events and _is_file_preview_url(
        request.referrer, record["id"], obj.key
    ):
        return None

    event.update(
        {
            # When:
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            # What:
            "bucket_id": str(obj.bucket_id),
            "file_id": str(obj.file_id),
            "file_key": obj.key,
            "size": obj.file.size,
            "recid": record["id"],
            "parent_recid": record.parent["id"],
            # Who:
            "referrer": request.referrer,
            **get_user(),
        }
    )
    return event


def record_view_event_builder(event, sender_app, **kwargs):
    """Build a record-view event.

    *Note* that this function assumes a request context by accessing properties of
    Flask's global ``request`` object.
    """
    assert "record" in kwargs
    record = kwargs["record"]

    is_published = getattr(record, "is_published", False)
    is_draft = getattr(record, "is_draft", True)

    # drop not published records
    if is_published and not is_draft:
        event.update(
            {
                # When:
                "timestamp": datetime.now(timezone.utc)
                .replace(tzinfo=None)
                .isoformat(),
                # What:
                "recid": record["id"],
                "parent_recid": record.parent["id"],
                # Who:
                "referrer": request.referrer,
                **get_user(),
                # TODO probably we can add more request context information here for
                #      extra filtering (e.g. URL or query params for discarding the event
                #      when it's a citation text export)
            }
        )
        return event
    return None


def check_if_via_api(event, sender_app, **kwargs):
    """Check if the event comes from an API request.

    *Note* that this function assumes a request context by accessing properties of
    Flask's global ``request`` object.
    """
    via_api = None
    if "via_api" in kwargs:
        via_api = kwargs["via_api"]
    else:
        # fallback heuristic: let's check if the request was made to our API URL
        via_api = request.url.startswith(current_app.config["SITE_API_URL"])

    event.update({"via_api": via_api})
    return event


def drop_if_via_api(event, sender_app, **kwargs):
    """Drop the event if it comes from the API."""
    if "via_api" not in event or not event["via_api"]:
        return event

    return None


def build_record_unique_id(event):
    """Build record unique identifier."""
    # NOTE: the 'unique_id' is used by the aggregators to know which events
    #       should be aggregated together... since we want to distinguish between
    #       API and UI events, this needs to be incorporated into the 'unique_id'
    prefix = "api" if event.get("via_api") else "ui"
    event["unique_id"] = f"{prefix}_{event['recid']}"
    return event
