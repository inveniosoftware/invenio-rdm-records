# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Tests for the RDM search dumper."""

from copy import deepcopy

from invenio_rdm_records.records.dumpers import (
    EDTFDumperExt,
    EDTFListDumperExt,
    SearchDumper,
)
from invenio_rdm_records.records.dumpers.subject_hierarchy import (
    SubjectHierarchyDumperExt,
)


class _FakeRecord(dict):
    """Minimal dict-based record stub for dumper tests."""

    model = None


def _dump(record_data, extensions):
    """Dump record data with the RDM search dumper."""
    record = _FakeRecord(deepcopy(record_data))
    dumper = SearchDumper(extensions=extensions)
    return record, dumper.dump(record, {})


def test_search_dumper_does_not_mutate_dates():
    """Dumping must not leak date_range into the original record.
    The search dumper used to copy lists shallowly, so EDTFListDumperExt mutated the original records metadata.dates
    items in place. The polluted record data then failed JSONSchema validation 'Additional properties are not allowed ('date_range' was
    unexpected)' on the next write.
    """
    record_data = {
        "metadata": {
            "publication_date": "2026-09-23",
            "dates": [
                {
                    "date": "2026-09-23",
                    "type": {"id": "updated"},
                    "description": "Dataset metadata reviewed and updated.",
                }
            ],
        }
    }
    record, dumped = _dump(
        record_data,
        [
            EDTFDumperExt("metadata.publication_date"),
            EDTFListDumperExt("metadata.dates", "date"),
        ],
    )

    # The dump itself must contain the computed ranges...
    assert dumped["metadata"]["dates"][0]["date_range"] == {
        "gte": "2026-09-23",
        "lte": "2026-09-23",
    }
    assert "publication_date_range" in dumped["metadata"]
    # ...but the original record must be untouched.
    assert "date_range" not in record["metadata"]["dates"][0]
    assert "publication_date_range" not in record["metadata"]
    assert record["metadata"]["dates"][0] == record_data["metadata"]["dates"][0]


def test_search_dumper_does_not_mutate_nested_list_items():
    """Dumping must not mutate deeply nested list items either."""
    record_data = {
        "metadata": {
            "funding": [
                {"award": {"subjects": [{"id": "x", "props": {"parents": "a,b"}}]}}
            ]
        }
    }
    record, dumped = _dump(record_data, [SubjectHierarchyDumperExt()])

    assert (
        "hierarchy" in dumped["metadata"]["funding"][0]["award"]["subjects"][0]["props"]
    )
    assert (
        "hierarchy"
        not in record["metadata"]["funding"][0]["award"]["subjects"][0]["props"]
    )
