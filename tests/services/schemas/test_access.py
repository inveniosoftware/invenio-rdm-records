# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-FileCopyrightText: 2020-2021 Northwestern University.
# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""Test metadata access schema."""

import pytest
from marshmallow.exceptions import ValidationError

from invenio_rdm_records.services.schemas.access import AccessSchema, EmbargoSchema


def test_embargo_load_no_until_is_valid():
    expected = {"active": False, "until": None, "reason": None}

    valid_no_until = {
        "active": False,
    }
    assert expected == EmbargoSchema().load(valid_no_until)

    valid_no_until = {
        "active": False,
        "until": None,
    }
    assert expected == EmbargoSchema().load(valid_no_until)


def test_embargo_dump_no_until_is_valid():
    valid_no_until = {
        "active": False,
    }
    assert valid_no_until == EmbargoSchema().dump(valid_no_until)

    expected = {
        "active": False,
    }
    valid_no_until = {
        "active": False,
        "until": None,
    }
    assert expected == EmbargoSchema().dump(valid_no_until)


def test_valid_full():
    valid_full = {
        "record": "public",
        "files": "restricted",
        "embargo": {"active": True, "until": "2120-10-06", "reason": "espionage"},
    }
    assert valid_full == AccessSchema().load(valid_full)


@pytest.mark.parametrize(
    "invalid_access,invalid_attr",
    [
        (
            {
                "files": "restricted",
                "embargo": {"active": True, "until": "2131-01-01", "reason": "secret!"},
            },
            "record",
        ),
        (
            {
                "record": "public",
                "embargo": {"active": True, "until": "2131-01-01", "reason": "secret!"},
            },
            "files",
        ),
        (
            {
                "record": "public",
                "files": "restricted",
                "embargo": {
                    "active": False,
                    "until": "2131-01-01",
                    "reason": "secret!",
                },
            },
            "embargo",
        ),
        (
            {
                "record": "public",
                "files": "restricted",
                "embargo": {"active": True, "until": "1999-01-01", "reason": "secret!"},
            },
            "embargo",
        ),
        (
            {
                "record": "invalid",
                "files": "restricted",
                "embargo": {
                    "active": False,
                    "until": "1999-01-01",
                    "reason": "secret!",
                },
            },
            "record",
        ),
        (
            {
                "record": "public",
                "files": "invalid",
                "embargo": {
                    "active": False,
                    "until": "1999-01-01",
                    "reason": "secret!",
                },
            },
            "files",
        ),
    ],
)
def test_invalid(invalid_access, invalid_attr):
    with pytest.raises(ValidationError) as e:
        AccessSchema().load(invalid_access)

    error_fields = e.value.messages.keys()
    assert len(error_fields) == 1
    assert invalid_attr in error_fields
