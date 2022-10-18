# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities fixture module."""

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDAlreadyExists

from .fixture import FixtureMixin


class CommunitiesFixture(FixtureMixin):
    """Communities fixture."""

    def create(self, entry):
        """Load a single community."""
        access_visibility = entry.get("access").get("visibility")
        slug = entry.get("slug")
        metadata_title = entry.get("metadata").get("title")

        community_data = {
            "access": {
                "visibility": access_visibility,
            },
            "slug": slug,
            "metadata": {
                "title": metadata_title,
            },
        }

        service = current_communities.service
        try:
            service.create(data=community_data, identity=system_identity)
        except PIDAlreadyExists:
            pass
