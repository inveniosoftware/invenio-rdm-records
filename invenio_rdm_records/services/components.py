# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service components."""

from invenio_records_resources.services.records.components import \
    ServiceComponent


# TODO: move into invenio-communities
class CommunitiesComponent(ServiceComponent):
    """Service component for communities integration."""


# TODO: move into invenio-stats
class StatsComponent(ServiceComponent):
    """Service component for stats integration."""


class AccessComponent(ServiceComponent):
    """Service component for access integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        validated_data = data.get('access', {})
        # TODO (Alex): replace with `record.access = ...`
        validated_data.setdefault('owned_by', [identity.id])
        record.update({'access': validated_data})

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        validated_data = data.get('access', {})
        # TODO (Alex): replace with `record.access = ...`
        validated_data.setdefault('owned_by', [identity.id])
        record.update({'access': validated_data})
