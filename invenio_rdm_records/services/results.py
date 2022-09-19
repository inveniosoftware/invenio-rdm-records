# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service results."""

from invenio_communities.communities.resolver import pick_fields
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.records.results import ExpandableField


class ParentCommunitiesExpandableField(ExpandableField):
    """Parent communities field."""

    def get_value_service(self, value):
        """Return the value and the service via entity resolvers."""
        return value, current_communities.service

    def pick(self, resolved_rec):
        """Pick fields defined in the entity resolver."""
        return pick_fields(resolved_rec)
