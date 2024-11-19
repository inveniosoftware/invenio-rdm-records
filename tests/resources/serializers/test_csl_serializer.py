# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from copy import deepcopy

from citeproc_styles import get_style_filepath

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.resources.serializers import (
    CSLJSONSerializer,
    StringCitationSerializer,
)
from invenio_rdm_records.resources.serializers.csl import get_citation_string
from invenio_rdm_records.resources.serializers.csl.schema import CSLJSONSchema


def test_csl_json_serializer(running_app, full_record_to_dict):
    """Test JSON CLS Serializer."""
    # if the record is created this field will be present
    full_record_to_dict["id"] = "12345-abcde"

    expected_data = {
        "DOI": "10.1234/12345-abcde",
        "abstract": "A description \nwith HTML tags",
        "author": [
            {"family": "Nielsen", "given": "Lars Holm"},
            {"family": "Tom", "given": "Blabin"},
        ],
        "id": "12345-abcde",
        "issued": {"date-parts": [["2018"], ["2020", "09"]]},
        "language": "dan",
        "publisher": "InvenioRDM",
        "title": "InvenioRDM",
        "type": "graphic",
        "version": "v1.0",
    }

    serializer = CSLJSONSerializer()
    serialized_record = serializer.dump_obj(full_record_to_dict)
    assert serialized_record == expected_data

    # test wrong publication date
    rec_wrong_date = deepcopy(full_record_to_dict)
    rec_wrong_date["metadata"]["publication_date"] = "wrong"
    expected = deepcopy(expected_data)
    del expected["issued"]  # missing

    assert serialized_record == expected_data


def test_citation_string_serializer_records_list(
    running_app,
    client,
    search_clear,
    minimal_record,
    superuser_identity,
):
    """Test Citation String Serializer for a list of records."""
    service = current_rdm_records.records_service
    default_style = StringCitationSerializer._default_style
    default_locale = StringCitationSerializer._default_locale
    headers = {"Accept": "text/x-bibliography"}

    expected_data = []
    for _ in range(3):
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(superuser_identity, draft.id)
        expected_record_data = get_citation_string(
            CSLJSONSchema().dump(record),
            record.id,
            locale=default_locale,
            style=get_style_filepath(default_style),
        )
        expected_data.append(expected_record_data)

    RDMRecord.index.refresh()

    response = client.get("/records", headers=headers)
    response_data = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain"

    for citation in expected_data:
        assert citation in response_data


def test_citation_string_serializer_record(
    running_app,
    client,
    search_clear,
    minimal_record,
    superuser_identity,
):
    """Test Citation String Serializer for single records."""
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)
    _id = record.id
    _url = f"/records/{_id}"
    headers = {"Accept": "text/x-bibliography"}

    default_style = StringCitationSerializer._default_style
    default_locale = StringCitationSerializer._default_locale

    test_cases = [
        (
            f"{_url}?style=3d-printing-in-medicine&locale=es-ES",
            "3d-printing-in-medicine",
            "es-ES",
            200,
        ),
        (f"{_url}?locale=es-ES", default_style, "es-ES", 200),
        (
            f"{_url}?style=3d-printing-in-medicine",
            "3d-printing-in-medicine",
            default_locale,
            200,
        ),
        (f"{_url}", default_style, default_locale, 200),
        (f"{_url}?style=Unknown_style", "Unknown_style", default_locale, 400),
        (f"{_url}?locale=Unknown_locale", default_style, default_locale, 200),
    ]

    for url, expected_style, expected_locale, expected_status in test_cases:
        response = client.get(url, headers=headers)
        assert response.status_code == expected_status

        body = response.get_data(as_text=True)

        if expected_status == 200:
            assert response.headers["content-type"] == "text/plain"
            expected_data = get_citation_string(
                CSLJSONSchema().dump(record),
                _id,
                locale=expected_locale,
                style=get_style_filepath(expected_style),
            )
            assert expected_data == body
        elif expected_status == 400:
            # in case of error, the response is JSON
            assert response.headers["content-type"] == "application/json"
            assert f"Citation string style not found." in body


def test_citation_string_serializer_empty_record(running_app, empty_record):
    """Test Citation String Serializer for an empty record."""

    expected_data = {}

    serializer = CSLJSONSchema()
    serialized_record = serializer.dump(empty_record)

    assert serialized_record == expected_data
