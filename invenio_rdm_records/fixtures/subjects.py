# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Affiliations fixtures module."""

from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from .fixture import FixtureMixin


class SubjectsFixture(FixtureMixin):
    """Affiliations fixture."""

    def create(self, entry):
        """Load a single subject."""
        service = current_service_registry.get("rdm-subjects")
        service.create(identity=system_identity, data=entry)
