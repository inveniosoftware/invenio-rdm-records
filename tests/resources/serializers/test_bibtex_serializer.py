# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers.bibtex import BibtexSerializer


@pytest.fixture(scope="function")
def updated_minimal_record(minimal_record):
    """Update fields (done after record create) for BibTex serializer."""
    minimal_record["access"]["status"] = "open"
    minimal_record["metadata"]["publication_date"] = "2023-03-13"
    minimal_record["created"] = "2024-12-17T00:00:00.000000+00:00"
    minimal_record["id"] = "abcde-fghij"

    for creator in minimal_record["metadata"]["creators"]:
        name = creator["person_or_org"].get("name")
        if not name:
            creator["person_or_org"]["name"] = "Name"

    return minimal_record


@pytest.fixture(scope="function")
def updated_full_record(full_record_to_dict):
    """Update fields (done after record create) for BibTex serializer."""
    full_record_to_dict["access"]["status"] = "embargoed"
    full_record_to_dict["metadata"]["publication_date"] = "2023-03/2024-02"
    full_record_to_dict["created"] = "2024-12-17T00:00:00.000000+00:00"
    full_record_to_dict["id"] = "abcde-fghij"
    full_record_to_dict["metadata"]["resource_type"]["id"] = "other"

    return full_record_to_dict


def test_bibtex_serializer_minimal_record(running_app, updated_minimal_record):
    """Test serializer for BibTex"""
    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@misc{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  month        = mar,",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_bibtex_serializer_full_record(running_app, updated_full_record):
    """Test serializer for BibTex"""
    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_full_record)

    expected_data = (
        "@misc{nielsen_2023_abcde-fghij,\n"
        "  author       = {Nielsen, Lars Holm and\n"
        "                  Tom, Blabin},\n"
        "  title        = {InvenioRDM},\n"
        "  month        = mar,\n"
        "  year         = 2023,\n"
        "  publisher    = {InvenioRDM},\n"
        "  version      = {v1.0},\n"
        "  doi          = {10.1234/12345-abcde},\n"
        "  url          = {https://doi.org/10.1234/12345-abcde},\n"
        "}"
    )

    assert serialized_record == expected_data


@pytest.mark.parametrize(
    "resource_type",
    [
        ("publication"),
        ("publication-annotationcollection"),
        ("publication-section"),
        ("publication-datamanagementplan"),
        ("publication-journal"),
        ("publication-patent"),
        ("publication-peerreview"),
        ("publication-deliverable"),
        ("publication-milestone"),
        ("publication-proposal"),
        ("publication-report"),
        ("publication-softwaredocumentation"),
        ("publication-taxonomictreatment"),
        ("publication-datapaper"),
        ("publication-dissertation"),
        ("publication-standard"),
        ("publication-other"),
        ("poster"),
        ("presentation"),
        ("event"),
        ("image"),
        ("image-figure"),
        ("image-plot"),
        ("image-drawing"),
        ("image-diagram"),
        ("image-photo"),
        ("image-other"),
        ("model"),
        ("video"),
        ("lesson"),
        ("software-computationalnotebook"),
        ("other"),
        ("physicalobject"),
        ("workflow"),
    ],
)
def test_misc_types(running_app, updated_minimal_record, resource_type):
    """Test bibtex misc formatter for each resource type."""
    updated_minimal_record["metadata"]["resource_type"]["id"] = resource_type
    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@misc{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  month        = mar,",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_conferencepaper(running_app, updated_minimal_record):
    """Test bibtex formatter for conference papers.

    It serializes into the following formats, depending on the data:

    - inproceedings
    - misc
    """
    updated_minimal_record["metadata"]["resource_type"][
        "id"
    ] = "publication-conferencepaper"

    # Force serialization into 'inproceedings'
    updated_minimal_record.update(
        {"custom_fields": {"imprint:imprint": {"title": "book title"}}}
    )
    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@inproceedings{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  booktitle    = {book title},",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "  month        = mar,",
            "}",
        ]
    )

    assert serialized_record == expected_data

    # Force serialization into 'misc'
    del updated_minimal_record["custom_fields"]["imprint:imprint"]
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@misc{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  month        = mar,",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_conferenceproceeding(
    running_app, updated_minimal_record
):
    """Test bibtex formatter for conference proceedings.

    It serializes into 'proceedings'.
    """
    updated_minimal_record["metadata"]["resource_type"][
        "id"
    ] = "publication-conferenceproceeding"

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@proceedings{brown_2023_abcde-fghij,",
            "  title        = {A Romans story},",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "  month        = mar,",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_book(running_app, updated_minimal_record):
    """Test bibtex formatter for books.

    It serializes into the following formats, depending on the data:

    - book
    - booklet
    """
    updated_minimal_record["metadata"]["resource_type"]["id"] = "publication-book"

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@book{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  publisher    = {Acme Inc},",
            "  year         = 2023,",
            "  month        = mar,",
            "}",
        ]
    )

    assert serialized_record == expected_data

    # Force serialization into 'booklet'
    del updated_minimal_record["metadata"]["publisher"]
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@booklet{brown_2023_abcde-fghij,",
            "  title        = {A Romans story},",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  month        = mar,",
            "  year         = 2023,",
            "}",
        ]
    )
    assert serialized_record == expected_data


def test_serialize_publication_article(running_app, updated_minimal_record):
    """Test bibtex formatter for articles.

    It serializes into 'article'.
    """
    updated_minimal_record["metadata"]["resource_type"]["id"] = "publication-article"

    updated_minimal_record.update(
        {"custom_fields": {"journal:journal": {"title": "journal title"}}}
    )

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@article{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  journal      = {journal title},",
            "  year         = 2023,",
            "  month        = mar,",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_preprint(running_app, updated_minimal_record):
    """Test bibtex formatter for preprints.

    It serializes into 'unpublished'.
    """
    updated_minimal_record["metadata"]["resource_type"]["id"] = "publication-preprint"

    updated_minimal_record.update(
        {
            "additional_descriptions": [
                {"type": {"id": "other"}, "description": "a description"}
            ]
        }
    )

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@unpublished{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  note         = {a description},",
            "  month        = mar,",
            "  year         = 2023,",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_thesis(running_app, updated_minimal_record):
    """Test bibtex formatter for thesis.

    It serializes into 'phdthesis'.
    """
    updated_minimal_record["metadata"]["resource_type"]["id"] = "publication-thesis"

    updated_minimal_record.update(
        {"custom_fields": {"thesis:university": "A university"}}
    )

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@phdthesis{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  school       = {A university},",
            "  year         = 2023,",
            "  month        = mar,",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_technicalnote(running_app, updated_minimal_record):
    """Test bibtex formatter for technical note.

    It serializes into 'manual'.
    """
    updated_minimal_record["metadata"]["resource_type"][
        "id"
    ] = "publication-technicalnote"

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@manual{brown_2023_abcde-fghij,",
            "  title        = {A Romans story},",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  month        = mar,",
            "  year         = 2023,",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_publication_workingpaper(running_app, updated_minimal_record):
    """Test bibtex formatter for working paper.

    It serializes into 'unpublished'.
    """
    updated_minimal_record["metadata"]["resource_type"][
        "id"
    ] = "publication-workingpaper"

    updated_minimal_record.update(
        {
            "additional_descriptions": [
                {"type": {"id": "other"}, "description": "a description"}
            ]
        }
    )

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@unpublished{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  note         = {a description},",
            "  month        = mar,",
            "  year         = 2023,",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_software(running_app, updated_minimal_record):
    """Test bibtex formatter for software.

    It serializes into 'software'.
    """
    updated_minimal_record["metadata"]["resource_type"]["id"] = "software"

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@software{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  month        = mar,",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "}",
        ]
    )

    assert serialized_record == expected_data


def test_serialize_dataset(running_app, updated_minimal_record):
    """Test bibtex formatter for dataset.

    It serializes into 'dataset'.
    """
    updated_minimal_record["metadata"]["resource_type"]["id"] = "dataset"

    serializer = BibtexSerializer()
    serialized_record = serializer.serialize_object(updated_minimal_record)

    expected_data = "\n".join(
        [
            "@dataset{brown_2023_abcde-fghij,",
            "  author       = {Name and",
            "                  Troy Inc.},",
            "  title        = {A Romans story},",
            "  month        = mar,",
            "  year         = 2023,",
            "  publisher    = {Acme Inc},",
            "}",
        ]
    )

    assert serialized_record == expected_data
