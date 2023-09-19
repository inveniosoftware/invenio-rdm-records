# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Record 'verified' system field."""

from invenio_records_resources.records.systemfields.calculated import CalculatedField


class IsVerifiedField(CalculatedField):
    """System field for calculating whether the record is verified."""

    def __init__(self, key=None):
        """Constructor."""
        super().__init__(key=key, use_cache=False)

    def calculate(self, record):
        """Calculate the ``is_verified`` property of the record."""
        owner = record.access.owner.resolve()
        if not owner:
            return False
        return owner.verified_at is not None
