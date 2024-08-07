# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from invenio_rdm_records.resources.serializers import (
    FAIRSignpostingProfileLvl2Serializer,
)


def test_signposting_serializer_full(running_app, full_record_to_dict):
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
                        "type": "application/linkset+json",
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
                        "href": "https://127.0.0.1:5000/records/12345-abcde/files/test.txt",  # noqa
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
                "anchor": "https://127.0.0.1:5000/records/12345-abcde/files/test.txt",
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

    serialized = FAIRSignpostingProfileLvl2Serializer().dump_obj(full_record_to_dict)

    assert expected == serialized


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
                        "type": "application/linkset+json",
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
