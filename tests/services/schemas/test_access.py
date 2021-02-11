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


def test_valid_full():
    valid_full = {
        "record": "public",
        "files": "restricted",
        "owned_by": [{"user": 1}],
        "embargo": {
            "active": True,
            "until": "2120-10-06",
            "reason": "espionage"
        },
    }
    assert valid_full == AccessSchema().load(valid_full)


@pytest.mark.parametrize("invalid_access,invalid_attr", [
    ({"files": "restricted", "owned_by": [{"user": 1}],
     "embargo": {"active": True, "until": "2131-01-01", "reason": "secret!"}},
     "record"),
    ({"record": "public", "owned_by": [{"user": 1}],
     "embargo": {"active": True, "until": "2131-01-01", "reason": "secret!"}},
     "files"),
    ({"record": "public", "files": "restricted", "owned_by": [1],
     "embargo": {"active": True, "until": "2131-01-01", "reason": "secret!"}},
     "owned_by"),
    ({"record": "public", "files": "restricted", "owned_by": [{"user": 1}],
     "embargo": {"active": False, "until": "2131-01-01", "reason": "secret!"}},
     "embargo"),
    ({"record": "public", "files": "restricted", "owned_by": [{"user": 1}],
     "embargo": {"active": True, "until": "1999-01-01", "reason": "secret!"}},
     "embargo"),
    ({"record": "invalid", "files": "restricted", "owned_by": [{"user": 1}],
     "embargo": {"active": False, "until": "1999-01-01", "reason": "secret!"}},
     "record"),
    ({"record": "public", "files": "invalid", "owned_by": [{"user": 1}],
     "embargo": {"active": False, "until": "1999-01-01", "reason": "secret!"}},
     "files"),
])
def test_invalid(invalid_access, invalid_attr):

    with pytest.raises(ValidationError) as e:
        AccessSchema().load(invalid_access)

    error_fields = e.value.messages.keys()
    assert len(error_fields) == 1
    assert invalid_attr in error_fields
