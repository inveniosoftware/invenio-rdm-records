# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test CFF serializer."""
from invenio_rdm_records.resources.serializers import CFFSerializer


def test_cff_serializer(running_app, full_record):
    """Test JSON CLS Serializer."""
    # if the record is created this field will be present
    full_record["id"] = "12345-abcde"
    full_record["metadata"]["resource_type"]["id"] = "software"
    ri = full_record["metadata"]["related_identifiers"]
    full_record["metadata"]["related_identifiers"] = [
        *ri,
        {
            "scheme": "url",
            "identifier": "https://github.com/citation-file-format/cff-converter-python",
            "resource_type": {"id": "software"},
            "relation_type": {"id": "issupplementto"},
        },
    ]

    serializer = CFFSerializer()
    serialized_record = serializer.serialize_object(full_record)
    assert serialized_record == (
        "abstract: <h1>A description</h1> <p>with HTML tags</p>\n"
        "authors:\n"
        "- affiliation: cern\n"
        "  family-names: Nielsen\n"
        "  given-names: Lars Holm\n"
        "  orcid: 0000-0001-8135-3489\n"
        "- affiliation: cern\n"
        "  family-names: Nielsen\n"
        "  given-names: Lars Holm\n"
        "  orcid: 0000-0001-8135-3489\n"
        "cff-version: 1.2.0\n"
        "date-released: 2018/2020-09\n"
        "doi: 10.1234/inveniordm.1234\n"
        "identifiers:\n"
        "- type: other\n"
        "  value: 1924MNRAS..84..308E\n"
        "keywords:\n"
        "- http://id.nlm.nih.gov/mesh/A-D000007\n"
        "- custom\n"
        "license:\n"
        "- cc-by-4.0\n"
        "license-url: https://customlicense.org/licenses/by/4.0/\n"
        "repository-code: "
        "https://github.com/citation-file-format/cff-converter-python\n"
        "title: InvenioRDM\n"
        "type: software\n"
        "version: v1.0\n"
    )
