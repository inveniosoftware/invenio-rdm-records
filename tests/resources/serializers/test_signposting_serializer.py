# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
# Copyright (C) 2024-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers import (
    FAIRSignpostingProfileLvl1Serializer,
    FAIRSignpostingProfileLvl2Serializer,
)


@pytest.fixture
def full_record_to_dict_signposting(full_record_to_dict):
    # raise ValueError("boom boom")
    full_record_to_dict["files"] = {
        "count": 1,
        "enabled": True,
        "entries": {
            "testé.txt": {
                "checksum": "md5:e795abeef2c38de2b064be9f6364ceae",
                "ext": "txt",
                "id": "d22bde05-5a36-48a3-86a7-acf2c4bb6f64",
                "key": "testé.txt",
                "metadata": None,
                "mimetype": "text/plain",
                "size": 9,
            },
        },
        "order": [],
        "total_bytes": 9,
    }
    return full_record_to_dict


def test_signposting_serializer_full(running_app, full_record_to_dict_signposting):
    expected = {
        "linkset": [
            # Landing page Link Context Object
            {
                "anchor": "https://127.0.0.1:5000/records/12345-abcde",
                "author": [{"href": "https://orcid.org/0000-0001-8135-3489"}],
                "cite-as": [{"href": "https://doi.org/10.1234/12345-abcde"}],
                "describedby": [
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/dcat+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/ld+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/marcxml+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.citationstyles.csl+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.datacite.datacite+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.datacite.datacite+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.geo+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.inveniordm.v1+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.inveniordm.v1.full+csv",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/vnd.inveniordm.v1.simple+csv",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/x-bibtex",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "application/x-dc+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/12345-abcde",
                        "type": "text/x-bibliography",
                    },
                ],
                "item": [
                    {
                        "href": "https://127.0.0.1:5000/records/12345-abcde/files/test%C3%A9.txt",  # noqa
                        "type": "text/plain",
                    }
                ],
                "license": [
                    {"href": "https://customlicense.org/licenses/by/4.0/"},
                    {"href": "https://creativecommons.org/licenses/by/4.0/legalcode"},
                ],
                "type": [
                    {"href": "https://schema.org/Photograph"},
                    {"href": "https://schema.org/AboutPage"},
                ],
            },
            # Content Resource (file) Link Context Object
            {
                "anchor": "https://127.0.0.1:5000/records/12345-abcde/files/test%C3%A9.txt",
                "collection": [
                    {
                        "href": "https://127.0.0.1:5000/records/12345-abcde",
                        "type": "text/html",
                    }
                ],
            },
            # Metadata Resource (mimetype format representation) Link Context Object
            {
                "anchor": "https://127.0.0.1:5000/api/records/12345-abcde",
                "describes": [
                    {
                        "href": "https://127.0.0.1:5000/records/12345-abcde",
                        "type": "text/html",
                    }
                ],
            },
        ]
    }

    serialized = FAIRSignpostingProfileLvl2Serializer().dump_obj(
        full_record_to_dict_signposting
    )

    assert expected == serialized


def test_signposting_lvl1_serializer_full(running_app, full_record_to_dict_signposting):
    ui_url = "https://127.0.0.1:5000/records/12345-abcde"
    api_url = "https://127.0.0.1:5000/api/records/12345-abcde"
    filename = "test%C3%A9.txt"

    expected = [
        f'<https://orcid.org/0000-0001-8135-3489> ; rel="author"',
        f'<https://doi.org/10.1234/12345-abcde> ; rel="cite-as"',
        f'<{api_url}> ; rel="describedby" ; type="application/dcat+xml"',
        f'<{api_url}> ; rel="describedby" ; type="application/json"',
        f'<{api_url}> ; rel="describedby" ; type="application/ld+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/marcxml+xml"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.citationstyles.csl+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.datacite.datacite+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.datacite.datacite+xml"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.geo+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.inveniordm.v1+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.inveniordm.v1.full+csv"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.inveniordm.v1.simple+csv"',
        f'<{api_url}> ; rel="describedby" ; type="application/x-bibtex"',
        f'<{api_url}> ; rel="describedby" ; type="application/x-dc+xml"',
        f'<{api_url}> ; rel="describedby" ; type="text/x-bibliography"',
        f'<{ui_url}/files/{filename}> ; rel="item" ; type="text/plain"',
        '<https://customlicense.org/licenses/by/4.0/> ; rel="license"',
        '<https://creativecommons.org/licenses/by/4.0/legalcode> ; rel="license"',
        '<https://schema.org/Photograph> ; rel="type"',
        '<https://schema.org/AboutPage> ; rel="type"',
        f'<{api_url}> ; rel="linkset" ; type="application/linkset+json"',
    ]

    serialized = FAIRSignpostingProfileLvl1Serializer().serialize_object(
        full_record_to_dict_signposting
    )

    assert expected == serialized.split(" , ")


def test_signposting_serializer_minimal(running_app, minimal_record_to_dict):
    expected = {
        "linkset": [
            # Landing page Link Context Object
            {
                "anchor": "https://127.0.0.1:5000/records/67890-fghij",
                # No author since no associated PID
                # No cite-as since no DOI
                "describedby": [
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/dcat+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/ld+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/marcxml+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.citationstyles.csl+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.datacite.datacite+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.datacite.datacite+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.geo+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.inveniordm.v1+json",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.inveniordm.v1.full+csv",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/vnd.inveniordm.v1.simple+csv",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/x-bibtex",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "application/x-dc+xml",
                    },
                    {
                        "href": "https://127.0.0.1:5000/api/records/67890-fghij",
                        "type": "text/x-bibliography",
                    },
                ],
                # No license
                "type": [
                    {"href": "https://schema.org/Photograph"},
                    {"href": "https://schema.org/AboutPage"},
                ],
            },
            # No Content Resource (file) Link Context Object
            # Metadata Resource (mimetype format representation) Link Context Object
            {
                "anchor": "https://127.0.0.1:5000/api/records/67890-fghij",
                "describes": [
                    {
                        "href": "https://127.0.0.1:5000/records/67890-fghij",
                        "type": "text/html",
                    }
                ],
            },
        ]
    }

    serialized = FAIRSignpostingProfileLvl2Serializer().dump_obj(minimal_record_to_dict)

    assert expected == serialized


def test_signposting_lvl1_serializer_minimal(running_app, minimal_record_to_dict):
    api_url = "https://127.0.0.1:5000/api/records/67890-fghij"

    expected = [
        # No author since no associated PID
        # No cite-as since no DOI
        f'<{api_url}> ; rel="describedby" ; type="application/dcat+xml"',
        f'<{api_url}> ; rel="describedby" ; type="application/json"',
        f'<{api_url}> ; rel="describedby" ; type="application/ld+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/marcxml+xml"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.citationstyles.csl+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.datacite.datacite+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.datacite.datacite+xml"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.geo+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.inveniordm.v1+json"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.inveniordm.v1.full+csv"',
        f'<{api_url}> ; rel="describedby" ; type="application/vnd.inveniordm.v1.simple+csv"',
        f'<{api_url}> ; rel="describedby" ; type="application/x-bibtex"',
        f'<{api_url}> ; rel="describedby" ; type="application/x-dc+xml"',
        f'<{api_url}> ; rel="describedby" ; type="text/x-bibliography"',
        # No files
        # No license
        '<https://schema.org/Photograph> ; rel="type"',
        '<https://schema.org/AboutPage> ; rel="type"',
        f'<{api_url}> ; rel="linkset" ; type="application/linkset+json"',
    ]

    serialized = FAIRSignpostingProfileLvl1Serializer().serialize_object(
        minimal_record_to_dict
    )

    assert expected == serialized.split(" , ")
