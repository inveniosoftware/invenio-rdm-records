# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers test fixtures."""

import pytest


@pytest.fixture
def parent_record():
    """Parent record metadata."""
    return {
        "pids": {
            "doi": {
                "identifier": "10.1234/inveniordm.1234.parent",
                "provider": "datacite",
                "client": "inveniordm",
            },
        }
    }


@pytest.fixture
def full_record(full_record, parent_record):
    """Full record metadata with added parent metadata."""
    full_record["parent"] = parent_record
    return full_record


@pytest.fixture
def enhanced_full_record(enhanced_full_record, parent_record):
    """Enhanced full record metadata with added parent metadata."""
    enhanced_full_record["parent"] = parent_record
    return enhanced_full_record


@pytest.fixture
def full_record_to_dict():
    """The to_dict() representation of a full record.

    THIS is the representation that a serializer gets as input.

    It's the static output of service().read().to_dict() (and equally projection in
    RecordList.hits), so
    - easier to test for specific id
    - faster test (no DB hit)
    - easier to make adjustments (e.g. removing DOI in the minimal_record_to_dict
      version)
    - easier to directly see content available when implementing a serializer
    """
    return {
        "access": {
            "embargo": {
                "active": True,
                "reason": "Only for medical doctors.",
                "until": "2131-01-01",
            },
            "files": "restricted",
            "record": "public",
            "status": "embargoed",
        },
        "created": "2023-11-14T18:30:55.738898+00:00",
        "custom_fields": {},
        "deletion_status": {
            "is_deleted": False,
            "status": "P",
        },
        "files": {
            "count": 1,
            "enabled": True,
            "entries": {
                "test.txt": {
                    "checksum": "md5:e795abeef2c38de2b064be9f6364ceae",
                    "ext": "txt",
                    "id": "d22bde05-5a36-48a3-86a7-acf2c4bb6f64",
                    "key": "test.txt",
                    "metadata": None,
                    "mimetype": "text/plain",
                    "size": 9,
                }
            },
            "order": [],
            "total_bytes": 9,
        },
        "id": "12345-abcde",
        "is_draft": False,
        "is_published": True,
        "links": {
            "access": "https://127.0.0.1:5000/api/records/12345-abcde/access",
            "access_links": "https://127.0.0.1:5000/api/records/12345-abcde/access/links",  # noqa
            "access_request": "https://127.0.0.1:5000/api/records/12345-abcde/access/request",  # noqa
            "access_users": "https://127.0.0.1:5000/api/records/12345-abcde/access/users",  # noqa
            "access_groups": "https://127.0.0.1:5000/api/records/12345-abcde/access/groups",  # noqa
            "archive": "https://127.0.0.1:5000/api/records/12345-abcde/files-archive",
            "archive_media": "https://127.0.0.1:5000/api/records/12345-abcde/media-files-archive",  # noqa
            "communities": "https://127.0.0.1:5000/api/records/12345-abcde/communities",
            "communities-suggestions": "https://127.0.0.1:5000/api/records/12345-abcde/communities-suggestions",  # noqa
            "doi": "https://handle.stage.datacite.org/10.1234/inveniordm.1234",
            "draft": "https://127.0.0.1:5000/api/records/12345-abcde/draft",
            "files": "https://127.0.0.1:5000/api/records/12345-abcde/files",
            "latest": "https://127.0.0.1:5000/api/records/12345-abcde/versions/latest",
            "latest_html": "https://127.0.0.1:5000/records/12345-abcde/latest",
            "media_files": "https://127.0.0.1:5000/api/records/12345-abcde/media-files",
            "parent": "https://127.0.0.1:5000/api/records/pgfpj-at058",
            "parent_doi": "https://127.0.0.1:5000/doi/10.1234/pgfpj-at058",
            "parent_html": "https://127.0.0.1:5000/records/pgfpj-at058",
            "requests": "https://127.0.0.1:5000/api/records/12345-abcde/requests",
            "reserve_doi": "https://127.0.0.1:5000/api/records/12345-abcde/draft/pids/doi",  # noqa
            "self": "https://127.0.0.1:5000/api/records/12345-abcde",
            "self_doi": "https://127.0.0.1:5000/doi/10.1234/inveniordm.1234",
            "self_html": "https://127.0.0.1:5000/records/12345-abcde",
            "self_iiif_manifest": "https://127.0.0.1:5000/api/iiif/record:12345-abcde/manifest",  # noqa
            "self_iiif_sequence": "https://127.0.0.1:5000/api/iiif/record:12345-abcde/sequence/default",  # noqa
            "versions": "https://127.0.0.1:5000/api/records/12345-abcde/versions",
        },
        "media_files": {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
        },
        "metadata": {
            "additional_descriptions": [
                {
                    "description": "Bla bla bla",
                    "lang": {
                        "id": "eng",
                        "title": {
                            "da": "Engelsk",
                            "en": "English",
                        },
                    },
                    "type": {
                        "id": "methods",
                        "title": {
                            "en": "Methods",
                        },
                    },
                },
            ],
            "additional_titles": [
                {
                    "lang": {
                        "id": "eng",
                        "title": {
                            "da": "Engelsk",
                            "en": "English",
                        },
                    },
                    "title": "a research data management platform",
                    "type": {
                        "id": "subtitle",
                        "title": {
                            "en": "Subtitle",
                        },
                    },
                },
            ],
            "contributors": [
                {
                    "affiliations": [
                        {
                            "id": "cern",
                            "name": "CERN",
                        },
                        {
                            "name": "TU Wien",
                        },
                    ],
                    "person_or_org": {
                        "family_name": "Nielsen",
                        "given_name": "Lars Holm",
                        "identifiers": [
                            {
                                "identifier": "0000-0001-8135-3489",
                                "scheme": "orcid",
                            }
                        ],
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                    },
                    "role": {
                        "id": "other",
                        "title": {
                            "en": "Other",
                        },
                    },
                },
                {
                    "person_or_org": {
                        "family_name": "Dirk",
                        "given_name": "Dirkin",
                        "name": "Dirk, Dirkin",
                        "type": "personal",
                    },
                    "role": {
                        "id": "other",
                        "title": {
                            "en": "Other",
                        },
                    },
                },
            ],
            "creators": [
                {
                    "affiliations": [
                        {
                            "id": "cern",
                            "name": "CERN",
                        },
                        {
                            "name": "free-text",
                        },
                    ],
                    "person_or_org": {
                        "family_name": "Nielsen",
                        "given_name": "Lars Holm",
                        "identifiers": [
                            {
                                "identifier": "0000-0001-8135-3489",
                                "scheme": "orcid",
                            },
                        ],
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                    },
                },
                {
                    "person_or_org": {
                        "family_name": "Tom",
                        "given_name": "Blabin",
                        "name": "Tom, Blabin",
                        "type": "personal",
                    },
                },
            ],
            "dates": [
                {
                    "date": "1939/1945",
                    "description": "A date",
                    "type": {
                        "id": "other",
                        "title": {
                            "en": "Other",
                        },
                    },
                },
            ],
            "description": "<h1>A description</h1> <p>with HTML tags</p>",
            "formats": [
                "application/pdf",
            ],
            "funding": [
                {
                    "award": {
                        "identifiers": [
                            {
                                "identifier": "https://sandbox.zenodo.org/",
                                "scheme": "url",
                            }
                        ],
                        "number": "111023",
                        "title": {
                            "en": "Launching of the research program on meaning processing",  # noqa
                        },
                    },
                    "funder": {
                        "id": "00k4n6c32",
                        "name": "European Commission",
                    },
                },
            ],
            "identifiers": [
                {
                    "identifier": "1924MNRAS..84..308E",
                    "scheme": "ads",
                }
            ],
            "languages": [
                {
                    "id": "dan",
                    "title": {
                        "da": "Dansk",
                        "en": "Danish",
                    },
                },
                {
                    "id": "eng",
                    "title": {
                        "da": "Engelsk",
                        "en": "English",
                    },
                },
            ],
            "locations": {
                "features": [
                    {
                        "description": "test location description",
                        "geometry": {
                            "coordinates": [
                                -32.94682,
                                -60.63932,
                            ],
                            "type": "Point",
                        },
                        "identifiers": [
                            {
                                "identifier": "Q39",
                                "scheme": "wikidata",
                            },
                            {
                                "identifier": "12345abcde",
                                "scheme": "geonames",
                            },
                        ],
                        "place": "test location place",
                    },
                ],
            },
            "publication_date": "2018/2020-09",
            "publisher": "InvenioRDM",
            "references": [
                {
                    "reference": "Nielsen et al,..",
                    "identifier": "0000 0001 1456 7559",
                    "scheme": "isni",
                },
            ],
            "related_identifiers": [
                {
                    "identifier": "10.1234/foo.bar",
                    "relation_type": {
                        "id": "iscitedby",
                        "title": {
                            "en": "Is cited by",
                        },
                    },
                    "resource_type": {
                        "id": "dataset",
                        "title": {
                            "en": "Dataset",
                        },
                    },
                    "scheme": "doi",
                },
            ],
            "resource_type": {
                "id": "image-photo",
                "title": {
                    "en": "Photo",
                },
            },
            "rights": [
                {
                    "description": {
                        "en": "A description",
                    },
                    "link": "https://customlicense.org/licenses/by/4.0/",
                    "title": {
                        "en": "A custom license",
                    },
                },
                {
                    "description": {
                        "en": "The Creative Commons Attribution license allows re-distribution and re-use of a licensed work on the condition that the creator is appropriately credited.",  # noqa
                    },
                    "id": "cc-by-4.0",
                    "props": {
                        "scheme": "spdx",
                        "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                    },
                    "title": {
                        "en": "Creative Commons Attribution 4.0 International",
                    },
                },
            ],
            "sizes": [
                "11 pages",
            ],
            "subjects": [
                {
                    "id": "http://id.nlm.nih.gov/mesh/A-D000007",
                    "scheme": "MeSH",
                    "subject": "Abdominal Injuries",
                },
                {
                    "subject": "custom",
                },
            ],
            "title": "InvenioRDM",
            "version": "v1.0",
        },
        "parent": {
            "access": {
                "grants": [],
                "links": [],
                "owned_by": {
                    "user": 2,
                },
                "settings": {
                    "accept_conditions_text": None,
                    "allow_guest_requests": False,
                    "allow_user_requests": False,
                    "secret_link_expiration": 0,
                },
            },
            "communities": {},
            "id": "pgfpj-at058",
            "pids": {
                "doi": {
                    "client": "datacite",
                    "identifier": "10.1234/pgfpj-at058",
                    "provider": "datacite",
                },
            },
        },
        "pids": {
            "doi": {
                "client": "datacite",
                "identifier": "10.1234/12345-abcde",
                "provider": "datacite",
            },
            "oai": {
                "identifier": "oai:invenio-rdm.com:12345-abcde",
                "provider": "oai",
            },
        },
        "revision_id": 4,
        "stats": {
            "all_versions": {
                "data_volume": 0.0,
                "downloads": 0,
                "unique_downloads": 0,
                "unique_views": 0,
                "views": 0,
            },
            "this_version": {
                "data_volume": 0.0,
                "downloads": 0,
                "unique_downloads": 0,
                "unique_views": 0,
                "views": 0,
            },
        },
        "status": "published",
        "updated": "2023-11-14T18:30:55.977122+00:00",
        "versions": {
            "index": 1,
            "is_latest": True,
            "is_latest_draft": True,
        },
    }


@pytest.fixture
def minimal_record_to_dict():
    """The to_dict() representation of a minimal record.

    THIS is the representation that a serializer gets as input.

    See full_record_to_dict above for motivation.
    """
    return {
        "access": {
            "embargo": {
                "active": False,
                "reason": None,
            },
            "files": "public",
            "record": "public",
            "status": "metadata-only",
        },
        "created": "2023-11-14T19:33:09.837080+00:00",
        "custom_fields": {},
        "deletion_status": {
            "is_deleted": False,
            "status": "P",
        },
        "files": {
            "count": 0,
            "enabled": False,  # Most tests don't care about files
            "entries": {},
            "order": [],
            "total_bytes": 0,
        },
        "id": "67890-fghij",
        "is_draft": False,
        "is_published": True,
        "links": {
            "access": "https://127.0.0.1:5000/api/records/67890-fghij/access",
            "access_links": "https://127.0.0.1:5000/api/records/67890-fghij/access/links",  # noqa
            "access_request": "https://127.0.0.1:5000/api/records/67890-fghij/access/request",  # noqa
            "access_users": "https://127.0.0.1:5000/api/records/67890-fghij/access/users",  # noqa
            "access_groups": "https://127.0.0.1:5000/api/records/67890-fghij/access/groups",  # noqa
            "archive": "https://127.0.0.1:5000/api/records/67890-fghij/files-archive",
            "archive_media": "https://127.0.0.1:5000/api/records/67890-fghij/media-files-archive",  # noqa
            "communities": "https://127.0.0.1:5000/api/records/67890-fghij/communities",
            "communities-suggestions": "https://127.0.0.1:5000/api/records/67890-fghij/communities-suggestions",  # noqa
            "doi": "https://handle.stage.datacite.org/10.1234/67890-fghij",
            "draft": "https://127.0.0.1:5000/api/records/67890-fghij/draft",
            "files": "https://127.0.0.1:5000/api/records/67890-fghij/files",
            "latest": "https://127.0.0.1:5000/api/records/67890-fghij/versions/latest",
            "latest_html": "https://127.0.0.1:5000/records/67890-fghij/latest",
            "media_files": "https://127.0.0.1:5000/api/records/67890-fghij/media-files",
            "parent": "https://127.0.0.1:5000/api/records/pgfpj-at058",
            "parent_doi": "https://127.0.0.1:5000/doi/10.1234/pgfpj-at058",
            "parent_html": "https://127.0.0.1:5000/records/pgfpj-at058",
            "requests": "https://127.0.0.1:5000/api/records/67890-fghij/requests",
            "reserve_doi": "https://127.0.0.1:5000/api/records/67890-fghij/draft/pids/doi",  # noqa
            "self": "https://127.0.0.1:5000/api/records/67890-fghij",
            "self_doi": "https://127.0.0.1:5000/doi/10.1234/67890-fghij",
            "self_html": "https://127.0.0.1:5000/records/67890-fghij",
            "self_iiif_manifest": "https://127.0.0.1:5000/api/iiif/record:67890-fghij/manifest",  # noqa
            "self_iiif_sequence": "https://127.0.0.1:5000/api/iiif/record:67890-fghij/sequence/default",  # noqa
            "versions": "https://127.0.0.1:5000/api/records/67890-fghij/versions",
        },
        "media_files": {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    },
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            "publisher": "Acme Inc",
            "resource_type": {
                "id": "image-photo",
                "title": {
                    "en": "Photo",
                },
            },
            "title": "A Romans story",
        },
        "parent": {
            "access": {
                "grants": [],
                "links": [],
                "owned_by": {
                    "user": 2,
                },
                "settings": {
                    "accept_conditions_text": None,
                    "allow_guest_requests": False,
                    "allow_user_requests": False,
                    "secret_link_expiration": 0,
                },
            },
            "communities": {},
            "id": "pgfpj-at058",
            "pids": {
                "doi": {
                    "client": "datacite",
                    "identifier": "10.1234/pgfpj-at058",
                    "provider": "datacite",
                },
            },
        },
        "pids": {
            "oai": {
                "identifier": "oai:invenio-rdm.com:67890-fghij",
                "provider": "oai",
            },
        },
        "revision_id": 4,
        "stats": {
            "all_versions": {
                "data_volume": 0.0,
                "downloads": 0,
                "unique_downloads": 0,
                "unique_views": 0,
                "views": 0,
            },
            "this_version": {
                "data_volume": 0.0,
                "downloads": 0,
                "unique_downloads": 0,
                "unique_views": 0,
                "views": 0,
            },
        },
        "status": "published",
        "updated": "2023-11-14T18:30:55.977122+00:00",
        "versions": {
            "index": 1,
            "is_latest": True,
            "is_latest_draft": True,
        },
    }
