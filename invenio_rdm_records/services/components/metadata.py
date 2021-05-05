# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for metadata."""

from copy import copy

from invenio_drafts_resources.services.records.components import \
    ServiceComponent


class MetadataComponent(ServiceComponent):
    """Service component for metadata."""

    new_version_skip_fields = ['publication_date', 'version']

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record.metadata = data.get('metadata', {})

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record.metadata = data.get('metadata', {})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        record.metadata = draft.get('metadata', {})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.metadata = record.get('metadata', {})

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.metadata = copy(record.get('metadata', {}))
        # Remove fields that should not be copied to the new version
        # (publication date and version)
        for f in self.new_version_skip_fields:
            draft.metadata.pop(f, None)
