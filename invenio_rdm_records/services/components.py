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


class AccessComponent(ServiceComponent):
    """Service component for access integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        if record is not None and not record.access.owners and identity.id:
            record.access.owners.add({"user": identity.id})

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        if record is not None and not record.access.owners and identity.id:
            record.access.owners.add({"user": identity.id})
