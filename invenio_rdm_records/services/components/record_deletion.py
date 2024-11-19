# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for record deletion."""

from flask import current_app
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n.proxies import current_i18n

from ...records.systemfields.deletion_status import RecordDeletionStatusEnum
from ...resources.serializers.csl import (
    CSLJSONSerializer,
    get_citation_string,
    get_style_location,
)


class RecordDeletionComponent(ServiceComponent):
    """Service component for record deletion."""

    def delete_record(self, identity, data=None, record=None, **kwargs):
        """Set the record's deletion status and tombstone information."""
        # If no `citation_text` has been supplied, create one
        if not data.get("citation_text", None):
            default_citation_style = current_app.config.get(
                "RDM_CITATION_STYLES_DEFAULT", "apa"
            )

            serializer = CSLJSONSerializer()
            style = get_style_location(default_citation_style)
            default_citation = get_citation_string(
                serializer.dump_obj(record),
                record.pid.pid_value,
                style,
                locale=current_i18n.language,
            )

            data["citation_text"] = default_citation

        # Set the record's deletion status and tombstone information
        record.deletion_status = RecordDeletionStatusEnum.DELETED
        record.tombstone = data

        # Set `removed_by` information for the tombstone
        record.tombstone.removed_by = identity.id

    def update_tombstone(self, identity, data=None, record=None, **kwargs):
        """Update the record's tombstone information."""
        record.tombstone = data

    def restore_record(self, identity, data=None, record=None, **kwargs):
        """Reset the record's deletion status and tombstone information."""
        record.deletion_status = RecordDeletionStatusEnum.PUBLISHED

        # Remove the tombstone information
        record.tombstone = None

        # Set a record to 'metadata only' if its files got cleaned up
        if not record.files.entries:
            record.files.enabled = False

    def mark_record(self, identity, data=None, record=None, **kwargs):
        """Mark the record for purge."""
        record.deletion_status = RecordDeletionStatusEnum.MARKED
        record.tombstone = record.tombstone

    def unmark_record(self, identity, data=None, record=None, **kwargs):
        """Unmark the record for purge, resetting it to soft-deleted state."""
        record.deletion_status = RecordDeletionStatusEnum.DELETED
        record.tombstone = record.tombstone
