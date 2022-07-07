# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for metadata."""

from copy import copy

from invenio_drafts_resources.services.records.components import ServiceComponent


class CustomFieldsComponent(ServiceComponent):
    """Service component for custom fields."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record["custom"] = data.get("custom", {})

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record["custom"] = data.get("custom", {})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        record["custom"] = draft.get("custom", {})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft["custom"] = record.get("custom", {})

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft["custom"] = copy(record.get("custom"), {})
        # Remove fields that should not be copied to the new version
        # (publication date and version)
        for f in self.new_version_skip_fields:
            draft.metadata.pop(f, None)
