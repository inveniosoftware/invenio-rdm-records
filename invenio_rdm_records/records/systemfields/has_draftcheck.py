# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record has draft check field.

The HasDraftCheckField is used to check if an associated draft exists for a
a record.
"""

from invenio_records.dictutils import dict_set
from invenio_records.systemfields import SystemField
from sqlalchemy.orm.exc import NoResultFound


class HasDraftCheckField(SystemField):
    """PID status field which checks against an expected status."""

    def __init__(self, draft_cls=None, key=None):
        """Initialize the PIDField.

        It stores the `record.has_draft` value in the secondary storage
        system's record or defaults to `False` if the `draft_cls` is not passed
        e.g Draft records.

        :param key: Attribute name of the HasDraftCheckField.
        :param draft_cls: The draft class to use for querying.
        """
        super().__init__(key=key)
        self.draft_cls = draft_cls

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            return self  # returns the field itself.

        # If not draft_cls is passed return False
        if self.draft_cls is None:
            return False

        try:
            self.draft_cls.get_record(record.id)
            return True
        except NoResultFound:
            return False

    def pre_dump(self, record, data, **kwargs):
        """Called before a record is dumped in a secondary storage system."""
        dict_set(data, self.key, record.has_draft)

    def post_load(self, record, data, **kwargs):
        """Called after a record is loaded from a secondary storage system."""
        record.pop(self.key, None)
