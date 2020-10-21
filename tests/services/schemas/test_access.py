# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata access schema."""

import pytest
from flask_babelex import lazy_gettext as _
from marshmallow.exceptions import ValidationError

from invenio_rdm_records.services.schemas.access import AccessSchema

from .test_utils import assert_raises_messages


def test_valid_full(vocabulary_clear):
    valid_full = {
        "metadata": False,
        "files": False,
        "owned_by": [1],
        "embargo_date": "2120-10-06",
        "access_right": "open",
        "access_condition": {
            "condition": "because it is needed",
            "default_link_validity": 30
        }
    }
    assert valid_full == AccessSchema().load(valid_full)


def test_invalid_access_right(vocabulary_clear):
    invalid_access_right = {
        "metadata": False,
        "files": False,
        "owned_by": [1],
        "access_right": "invalid value"
    }

    assert_raises_messages(
        lambda: AccessSchema().load(invalid_access_right),
        {
            "access_right": [_(
                "Invalid value. Choose one of ['closed', 'embargoed', "
                "'open', 'restricted']."
            )]
        }
    )


@pytest.mark.parametrize("invalid_access,missing_attr", [
    ({"metadata": False, "files": False, "access_right": "open"}, "owned_by"),
    ({"metadata": False, "files": False, "owned_by": [1]}, "access_right"),
    ({"metadata": False, "owned_by": [1], "access_right": "open"}, "files"),
    ({"files": False, "owned_by": [1], "access_right": "open"}, "metadata")
])
def test_invalid(invalid_access, missing_attr):

    with pytest.raises(ValidationError) as e:
        AccessSchema().load(invalid_access)

        error_fields = e.value.messages.keys()
        assert len(error_fields) == 1
        assert missing_attr in error_fields
