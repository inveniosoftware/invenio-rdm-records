# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import json
from copy import deepcopy

import pytest

from invenio_rdm_records.resources.serializers import UIJSONSerializer


def _add_affiliation_name(creatibutors):
    for idx_c, creator in enumerate(creatibutors):
        affiliations = creatibutors[idx_c]["affiliations"]
        for idx_aff, affiliation in enumerate(affiliations):
            name = creatibutors[idx_c]["affiliations"][idx_aff].get("id")
            if name:
                name = name.upper()
                creatibutors[idx_c]["affiliations"][idx_aff]["name"] = name
            if "role" in creatibutors[idx_c]:
                creatibutors[idx_c]["role"]["title"] = {
                    "en": creatibutors[idx_c]["role"]["id"]
                }


@pytest.fixture(scope="function")
def full_to_dict_record(full_record):
    """Full record dereferenced data, as is expected by the UI serializer."""
    # TODO: Converge this and full record over time
    to_dict_record = deepcopy(full_record)

    to_dict_record["metadata"]["languages"] = [
        {"id": "dan", "title": {"en": "Danish"}},
        {"id": "eng", "title": {"en": "English"}},
    ]

    to_dict_record["metadata"]["resource_type"] = {
        "id": "publication-article",
        "title": {"en": "Journal article"},
    }

    to_dict_record["metadata"]["subjects"] = [
        {"id": "A-D000007", "title": {"en": "Abdominal Injuries"}},
        {"id": "A-D000008", "title": {"en": "Abdominal Neoplasms"}},
    ]

    to_dict_record["metadata"]["related_identifiers"] = [
        {
            "identifier": "10.1234/foo.bar",
            "resource_type": {"id": "dataset", "title": {"en": "Dataset"}},
            "relation_type": {"id": "iscitedby", "title": {"en": "Is cited by"}},
            "scheme": "doi",
        }
    ]

    to_dict_record["metadata"]["funding"] = [
        {
            "funder": {
                "id": "00k4n6c32",
                "name": "EC",
                "title": {"en": "European Commission", "fr": "Commission Européenne"},
                "country": "BE",
            },
            "award": {
                "id": "00k4n6c32",
                "identifiers": [
                    {
                        "identifier": "000000012156142X",
                        "scheme": "isni",
                    },
                    {
                        "identifier": "00k4n6c32",
                        "scheme": "ror",
                    },
                ],
                "name": "European Commission",
                "title": {
                    "en": "European Commission",
                    "fr": "Commission européenne",
                },
                "country": "BE",
            },
        }
    ]

    _add_affiliation_name(to_dict_record["metadata"]["creators"])
    _add_affiliation_name(to_dict_record["metadata"]["contributors"])

    to_dict_record["access"]["status"] = "embargoed"

    return to_dict_record


def test_ui_serializer(app, full_to_dict_record):
    expected_data = {
        "access_status": {
            "description_l10n": "The files will be made publicly available on "
            "January 1, 2131.",
            "icon": "outline clock",
            "id": "embargoed",
            "title_l10n": "Embargoed",
            "embargo_date_l10n": "January 1, 2131",
            "message_class": "warning",
        },
        "contributors": {
            "affiliations": [[1, "CERN", "cern"]],
            "contributors": [
                {
                    "affiliations": [[1, "CERN"]],
                    "person_or_org": {
                        "family_name": "Nielsen",
                        "given_name": "Lars Holm",
                        "identifiers": [
                            {"identifier": "0000-0001-8135-3489", "scheme": "orcid"}
                        ],
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                    },
                    "role": {"id": "other", "title": "other"},
                }
            ],
        },
        "creators": {
            "affiliations": [[1, "CERN", "cern"], [2, "free-text", None]],
            "creators": [
                {
                    "affiliations": [[1, "CERN"], [2, "free-text"]],
                    "person_or_org": {
                        "family_name": "Nielsen",
                        "given_name": "Lars Holm",
                        "identifiers": [
                            {"identifier": "0000-0001-8135-3489", "scheme": "orcid"}
                        ],
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                    },
                }
            ],
        },
        "publication_date_l10n_long": "January 2018 – September 2020",
        "publication_date_l10n_medium": "Jan 2018 – Sep 2020",
        "resource_type": {"id": "publication-article", "title_l10n": "Journal article"},
        "additional_titles": [
            {
                "lang": {"id": "eng"},
                "title": "a research data management platform",
                "type": {"id": "subtitle"},
            }
        ],
        "additional_descriptions": [
            {
                "description": "Bla bla bla",
                "lang": {"id": "eng"},
                "type": {"id": "methods"},
            }
        ],
        "languages": [
            {"id": "dan", "title_l10n": "Danish"},
            {"id": "eng", "title_l10n": "English"},
        ],
        "dates": [
            {"date": "1939/1945", "description": "A date", "type": {"id": "other"}}
        ],
        "rights": [
            {
                "description_l10n": "A description",
                "link": "https://customlicense.org/licenses/by/4.0/",
                "title_l10n": "A custom license",
            },
            {"id": "cc-by-4.0"},
        ],
        "related_identifiers": [
            {
                "identifier": "10.1234/foo.bar",
                "relation_type": {"id": "iscitedby", "title_l10n": "Is cited by"},
                "resource_type": {"id": "dataset", "title_l10n": "Dataset"},
                "scheme": "doi",
            }
        ],
        "description_stripped": "A description \nwith HTML tags",
        "version": "v1.0",
        "funding": [
            {
                "award": {
                    "id": "00k4n6c32",
                    "identifiers": [
                        {"identifier": "000000012156142X", "scheme": "isni"},
                        {"identifier": "00k4n6c32", "scheme": "ror"},
                    ],
                    "title_l10n": "European Commission",
                },
                "funder": {
                    "country": "BE",
                    "id": "00k4n6c32",
                    "name": "EC",
                    "title_l10n": "European Commission",
                },
            }
        ],
    }

    serialized_record = UIJSONSerializer().dump_obj(full_to_dict_record)
    assert serialized_record["ui"] == expected_data

    serialized_records = UIJSONSerializer().serialize_object_list(
        {"hits": {"hits": [full_to_dict_record]}}
    )
    assert json.loads(serialized_records)["hits"]["hits"][0]["ui"] == expected_data
