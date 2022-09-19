# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test rights schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema, RightsSchema


def test_valid_full_free_text(running_app):
    valid_full = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "description": {"en": "A description"},
        "link": "https://creativecommons.org/licenses/by/4.0/",
    }
    assert valid_full == RightsSchema().load(valid_full)


def test_valid_minimal_free_text(running_app):
    valid_minimal = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
    }
    assert valid_minimal == RightsSchema().load(valid_minimal)


def test_valid_minimal_vocab(running_app):
    valid_minimal = {
        "id": "cc-by-4.0",
    }
    assert valid_minimal == RightsSchema().load(valid_minimal)


def test_invalid_extra_right(running_app):
    invalid_extra = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "scheme": "spdx",
        "identifier": "cc-by-4.0",
        "uri": "https://creativecommons.org/licenses/by/4.0/",
        "extra": "field",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_extra)


def test_invalid_url(running_app):
    invalid_url = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "description": {"en": "A description"},
        "link": "creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_title(running_app):
    invalid_url = {
        "title": {"ena": "Creative Commons Attribution 4.0 International"},
        "description": {"en": "A description"},
        "link": "creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_multiple_title(running_app):
    invalid_url = {
        "title": {
            "en": "Creative Commons Attribution 4.0 International",
            "es": "Creative Commons Attribution 4.0 International ES",
        },
        "description": {"en": "A description"},
        "link": "creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_description(running_app):
    invalid_url = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "description": {"en1": "A description"},
        "link": "creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_multiple_description(running_app):
    invalid_url = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "description": {"en": "A description", "es": "A description ES"},
        "link": "creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_id_and_title(running_app):
    invalid_url = {
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "description": {"en": "A description"},
        "id": "cc-by-4.0",
        "link": "creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_vocab(running_app):
    invalid_url = {"id": "cc-by-4.0", "link": "creativecommons.org/licenses/by/4.0/"}
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


def test_invalid_structure(running_app):
    invalid_structure = {
        "title": "Creative Commons Attribution 4.0 International",
        "description": {"en": "A description"},
        "link": "https://creativecommons.org/licenses/by/4.0/",
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_structure)


@pytest.mark.parametrize(
    "rights",
    [
        ([]),
        (
            [
                {
                    "title": {"en": "Custom license"},
                    "description": {"en": "Custom description"},
                    "link": "https://custom.org/licenses/by/4.0/",
                },
                {
                    "id": "cc-by-4.0",
                },
            ]
        ),
    ],
)
def test_valid_rights(running_app, rights, minimal_record):
    metadata = minimal_record["metadata"]
    # NOTE: this is done to get possible load transformations out of the way
    metadata = MetadataSchema().load(metadata)
    metadata["rights"] = rights

    assert metadata == MetadataSchema().load(metadata)
