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
