# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM requests decorators."""

import copy
from functools import wraps

from invenio_records_resources.services import ConditionalLink, LinksTemplate
from invenio_requests import current_requests_service

from ..services.review.links import RecordEndpointLinkFromRequest


def request_next_link(**kwargs):
    """Add the `next_html` extra link to the request item.

    This approach was taken because `ReviewService` returns a `RequestItem`
    i.e., its config doesn't control the links of the result item generated.
    """

    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            request_item = f(self, *args, **kwargs)

            config_of_requests_service = current_requests_service.config
            links_item_w_next_html = copy.deepcopy(
                config_of_requests_service.links_item
            )
            links_item_w_next_html["next_html"] = ConditionalLink(
                # obj is the request here
                cond=lambda obj, ctx: obj.is_open,  # i.e. has review request
                # just the self_html link of the request
                if_=links_item_w_next_html["self_html"],
                else_=RecordEndpointLinkFromRequest(
                    "invenio_app_rdm_records.record_detail"
                ),
            )
            new_links_tpl = LinksTemplate(
                links_item_w_next_html,
                # to avoid reaching for private properties we reproduce what
                # RequestsService.links_item_tpl does using only public interfaces.
                # We could make LinksTemplate.context public as an alternative/in the
                # future.
                context={
                    "permission_policy_cls": (
                        config_of_requests_service.permission_policy_cls
                    ),
                },
            )
            request_item.links_tpl = new_links_tpl

            return request_item

        return inner

    return decorator
