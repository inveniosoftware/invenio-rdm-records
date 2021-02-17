# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


"""Record status field."""

from invenio_records.systemfields import SystemField


class RecordStatusField(SystemField):
    """Record status field which checks if a record is published or draft.

    The dumped status is used to display uniquely the mixed list of published
    and draft records in case a published record is being edited thus has a
    draft associated with it.

    The record has:
        `PUBLISHED_STATUS`: the record has set the `has_draft` attribute.
        `DRAFT_STATUS`: the record hasn't set the `has_draft` attribute.
    """

    DRAFT_STATUS = 'draft'
    PUBLISHED_STATUS = 'published'

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            return self  # returns the field itself.
        # Draft records don't have the attribute `has_draft`
        is_record = hasattr(record, 'has_draft')
        if is_record:
            return self.PUBLISHED_STATUS
        else:
            return self.DRAFT_STATUS

    def pre_dump(self, record, **kwargs):
        """Called before a record is dumped."""
        record[self.key] = getattr(record, 'status')
