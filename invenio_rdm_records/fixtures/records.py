# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-FileCopyrightText: 2023 Northwestern University.
# SPDX-License-Identifier: MIT

"""Communities fixture module."""

from invenio_access.permissions import system_user_id

from .fixture import FixtureMixin


class RecordsFixture(FixtureMixin):
    """Records fixture."""

    def create(self, entry):
        """Load a single record."""
        self.create_record(system_user_id, entry, publish=True)
