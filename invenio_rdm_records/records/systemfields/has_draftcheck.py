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

from invenio_records.systemfields import SystemField
from sqlalchemy.orm.exc import NoResultFound


class HasDraftCheckField(SystemField):
    """PID status field which checks against an expected status."""

    def __init__(self, draft_cls, key=None):
        """Initialize the PIDField.

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
        try:
            self.draft_cls.get_record(record.id)
            return True
        except NoResultFound:
            return False
