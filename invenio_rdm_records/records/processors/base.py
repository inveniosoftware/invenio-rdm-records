# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-License-Identifier: MIT

"""Record files processor base."""


class RecordFilesProcessor:
    """Base class for record files processors."""

    def _can_process(self, draft, record):
        """Determine if this processor can process a given record file."""
        return False

    def _process(self, draft, record, uow=None):
        """Process a record file."""
        pass

    def __call__(self, draft, record, uow=None):
        """Call method."""
        if self._can_process(draft, record):
            self._process(draft, record, uow=uow)
