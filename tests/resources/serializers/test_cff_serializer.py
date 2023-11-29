# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CFF serializer tests."""
from invenio_rdm_records.resources.serializers import (
    CFFSerializer,
)


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
    assert serialized_record
