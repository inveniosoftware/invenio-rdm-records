# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities fixture module."""

from invenio_access.permissions import system_user_id

from .fixture import FixtureMixin


class RecordsFixture(FixtureMixin):
    """Records fixture."""

    def create(self, entry):
        """Load a single record."""
        self.create_record(system_user_id, entry, publish=True)
