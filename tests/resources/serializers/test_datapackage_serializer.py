# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Open Knowledge Foundation
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from invenio_rdm_records.resources.serializers.datapackage import DataPackageSerializer


def test_data_package_serializer_empty_record():
    serializer = DataPackageSerializer()
    serialized_record = serializer.dump_obj({})
    assert serialized_record == {
        "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
        "resources": [],
    }


def test_data_package_serializer_minimal_record(minimal_record_to_dict):
    serializer = DataPackageSerializer()
    serialized_record = serializer.dump_obj(minimal_record_to_dict)
    assert serialized_record == {
        "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
        "id": "https://handle.stage.datacite.org/10.1234/67890-fghij",
        "name": "67890-fghij",
        "title": "A Romans story",
        "created": "2023-11-14T19:33:09.837080+00:00",
        "homepage": "https://127.0.0.1:5000/records/67890-fghij",
        "resources": [],
        "contributors": [
            {
                "familyName": "Brown",
                "givenName": "Troy",
                "roles": ["creator"],
            },
            {
                "roles": ["creator"],
                "title": "Troy Inc.",
            },
        ],
    }


def test_data_package_serializer_full_record(full_record_to_dict):
    serializer = DataPackageSerializer()
    serialized_record = serializer.dump_obj(full_record_to_dict)
    assert serialized_record == {
        "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
        "id": "https://handle.stage.datacite.org/10.1234/inveniordm.1234",
        "name": "12345-abcde",
        "title": "InvenioRDM",
        "description": "<h1>A description</h1> <p>with HTML tags</p>",
        "version": "v1.0",
        "created": "2023-11-14T18:30:55.738898+00:00",
        "homepage": "https://127.0.0.1:5000/records/12345-abcde",
        "keywords": [
            "Abdominal Injuries",
            "custom",
        ],
        "resources": [
            {
                "name": "test.txt",
                "path": "https://127.0.0.1:5000/records/12345-abcde/files/test.txt",
                "format": "txt",
                "mimetype": "text/plain",
                "bytes": 9,
                "hash": "md5:e795abeef2c38de2b064be9f6364ceae",
            },
        ],
        "licenses": [
            {
                "name": "cc-by-4.0",
                "path": "https://creativecommons.org/licenses/by/4.0/legalcode",
                "title": "Creative Commons Attribution 4.0 International",
            },
        ],
        "contributors": [
            {
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "organization": "CERN",
                "roles": ["creator"],
                "title": "Nielsen, Lars Holm",
            },
            {
                "familyName": "Tom",
                "givenName": "Blabin",
                "roles": ["creator"],
                "title": "Tom, Blabin",
            },
            {
                "familyName": "Nielsen",
                "givenName": "Lars Holm",
                "organization": "CERN",
                "roles": ["other"],
                "title": "Nielsen, Lars Holm",
            },
            {
                "familyName": "Dirk",
                "givenName": "Dirkin",
                "roles": ["other"],
                "title": "Dirk, Dirkin",
            },
        ],
    }
