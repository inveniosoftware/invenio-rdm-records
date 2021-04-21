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

from invenio_rdm_records.services.schemas.metadata import MetadataSchema, \
    RightsSchema


def test_valid_full():
    valid_full = {
        "title": "Creative Commons Attribution 4.0 International",
        "description": "A description",
        "link": "https://creativecommons.org/licenses/by/4.0/"
    }
    assert valid_full == RightsSchema().load(valid_full)


def test_valid_minimal():
    valid_minimal = {
        "id": "cc-by-4.0",
    }
    assert valid_minimal == RightsSchema().load(valid_minimal)


def test_invalid_extra_right():
    invalid_extra = {
        "title": "Creative Commons Attribution 4.0 International",
        "scheme": "spdx",
        "identifier": "cc-by-4.0",
        "uri": "https://creativecommons.org/licenses/by/4.0/",
        "extra": "field"
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_extra)


def test_invalid_url():
    invalid_url = {
        "title": "Creative Commons Attribution 4.0 International",
        "description": "A description",
        "link": "creativecommons.org/licenses/by/4.0/"
    }
    with pytest.raises(ValidationError):
        RightsSchema().load(invalid_url)


@pytest.mark.parametrize("rights", [
    ([]),
    ([{
        "title": "Creative Commons Attribution 4.0 International",
        "scheme": "spdx",
        "identifier": "cc-by-4.0",
        "link": "https://creativecommons.org/licenses/by/4.0/"
    }, {
        "title": "Copyright (C) 2020. All rights reserved."
    }])
])
def test_valid_rights(rights, minimal_record, vocabulary_clear):
    metadata = minimal_record['metadata']
    # NOTE: this is done to get possible load transformations out of the way
    metadata = MetadataSchema().load(metadata)
    metadata['rights'] = rights

    assert metadata == MetadataSchema().load(metadata)
