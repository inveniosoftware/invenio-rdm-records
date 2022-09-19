# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for metadata."""

from copy import copy

from invenio_drafts_resources.services.records.components import ServiceComponent


class MetadataComponent(ServiceComponent):
    """Service component for metadata."""

    field = "metadata"
    new_version_skip_fields = ["publication_date", "version"]

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        setattr(record, self.field, data.get(self.field, {}))

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        setattr(record, self.field, data.get(self.field, {}))

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        setattr(record, self.field, draft.get(self.field, {}))

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        setattr(draft, self.field, record.get(self.field, {}))

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        setattr(draft, self.field, copy(record.get(self.field, {})))
        # Remove fields that should not be copied to the new version
        # (publication date and version)
        field_values = getattr(draft, self.field)
        for f in self.new_version_skip_fields:
            field_values.pop(f, None)
