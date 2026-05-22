# SPDX-FileCopyrightText: 2023 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test combined subjects dumper."""

from copy import deepcopy

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.records.api import RDMParent


def test_combined_subjects_dumper(running_app, db, minimal_record):
    input_subjects = [
        {"id": "http://id.nlm.nih.gov/mesh/A-D000007"},
        {"subject": "Capybara"},
    ]
    minimal_record["metadata"]["subjects"] = input_subjects
    parent = RDMParent.create({})

    cases = []
    for api_cls in [RDMDraft, RDMRecord]:
        data_input = deepcopy(minimal_record)
        api_instance = api_cls.create(data_input, parent=parent)
        dump = api_instance.dumps()
        cases.append((dump, api_cls))

    expected_combined_subjects = [
        "MeSH::Abdominal Injuries",
        "Capybara",
    ]
    for dump, api_cls in cases:
        assert expected_combined_subjects == dump["metadata"]["combined_subjects"]

        loaded = api_cls.loads(dump)
        assert "combined_subjects" not in loaded["metadata"]
        assert "subjects" in loaded["metadata"]
