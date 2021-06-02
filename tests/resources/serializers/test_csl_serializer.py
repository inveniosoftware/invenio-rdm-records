
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers import CSLJSONSerializer


def test_csl_serializer(
        running_app, full_record, vocabulary_clear):
    """Test serializer to DayaCide 4.3 JSON"""
    # if the record is created this field will be present
    full_record["id"] = "12345-abcde"

    expected_data = {
        "publisher": "InvenioRDM",
        "DOI": "10.5281/inveniordm.1234",
        "language": "dan",
        "title": "InvenioRDM",
        "issued": {"date-parts": [["2018"], ["2020", "09"]]},
        "abstract": "Test",
        "author": [{
            "family": "Nielsen, Lars Holm",
        }],
        "note": "Funding by European Commission ROR 1234.",
        "version": "v1.0",
        "type": "graphic",
        "id": "12345-abcde",
    }

    serializer = CSLJSONSerializer()
    serialized_record = serializer.dump_one(full_record)

    assert serialized_record == expected_data
