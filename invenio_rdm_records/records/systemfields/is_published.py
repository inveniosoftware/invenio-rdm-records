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
from invenio_records_resources.records.systemfields import PIDStatusCheckField


class IsPublishedField(PIDStatusCheckField):
    """Adds a `pre_dump` hook to pid status check field."""

    def pre_dump(self, record, data, **kwargs):
        """Called before a record is dumped in a secondary storage system."""
        dict_set(
            data,
            self.attr_name,
            getattr(record, self.attr_name)
        )
