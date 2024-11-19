# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service config."""

from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base import ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig

from .links import CollectionLink
from .results import CollectionItem, CollectionList
from .schema import CollectionSchema


class CollectionServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Collections service configuration."""

    result_item_cls = CollectionItem
    result_list_cls = CollectionList
    service_id = "collections"
    permission_policy_cls = FromConfig(
        "COMMUNITIES_PERMISSION_POLICY", default=CommunityPermissionPolicy
    )
    schema = CollectionSchema

    links_item = {
        "search": CollectionLink("/api/collections/{id}/records"),
        "self_html": ConditionalLink(
            cond=lambda coll, ctx: coll.community,
            if_=CollectionLink(
                "/communities/{community}/collections/{tree}/{collection}"
            ),
            else_=CollectionLink("/collections/{tree}/{collection}"),
        ),
    }
