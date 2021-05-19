# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for metadata."""

from copy import copy

from invenio_drafts_resources.services.records.components import \
    ServiceComponent


class RelationsComponent(ServiceComponent):
    """Base service component."""

    def read(self, identity, record=None):
        """Read record handler."""
        record.relations.dereference()

    def read_draft(self, identity, draft=None):
        """Read draft handler."""
        draft.relations.dereference()
