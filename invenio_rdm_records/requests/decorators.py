# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM requests decorators."""

from functools import wraps

from invenio_requests import current_requests_service
from invenio_requests.services.requests.links import RequestLink, RequestLinksTemplate

from ..services.review.links import RequestRecordLink


def request_next_link(**kwargs):
    """Add the `next_html` extra link to the request item."""

    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            request_item = f(self, *args, **kwargs)

            # check if the request is still open, or accepted (closed)
            has_review_request = request_item._record.is_open
            if has_review_request:
                next_html = RequestLink("{+ui}/me/requests/{id}")
            else:
                next_html = RequestRecordLink("{+ui}/records/{record_id}")

            # add the `next_html` link to help the UI to decide where to go next
            prev_item_tpl = current_requests_service.links_item_tpl
            links_item = dict(
                **prev_item_tpl._links,
                next_html=next_html,
            )
            links_item_tpl = RequestLinksTemplate(
                links_item,
                prev_item_tpl._action_link,
                context=prev_item_tpl._context,
            )
            request_item.links_tpl = links_item_tpl
            return request_item

        return inner

    return decorator
