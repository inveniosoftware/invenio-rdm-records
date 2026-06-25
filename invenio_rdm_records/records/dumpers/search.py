# SPDX-FileCopyrightText: 2026 TU Wien.
# SPDX-License-Identifier: MIT

"""Faster search dumper that runs a faster deep-ish copy of the data before dumping."""

from invenio_records.dumpers import SearchDumper as BaseSearchDumper

from ...utils import very_simple_deepcopy


class SearchDumper(BaseSearchDumper):
    """Search dumper that creates a faster deep-ish copy of the data before dumping.

    In this version of the search dumper, we replace ``copy.deepcopy()`` with a simpler
    copy deep-ish copy mechanism that still satisfies our expectations, for performance
    gains.
    """

    def _copy_record(self, record):
        """Create a simpler version of a deepcopy for the record."""
        return very_simple_deepcopy(dict(record))

    def _copy_data(self, data):
        """Create a simpler version of a deepcopy for the record."""
        return very_simple_deepcopy(data)
