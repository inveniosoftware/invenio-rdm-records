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

from invenio_rdm_records.schemas.access import AccessSchemaV1

from .test_utils import assert_raises_messages


def test_valid_full(vocabulary_clear):
    valid_full = {
        "metadata_restricted": False,
        "files_restricted": False,
        "owners": [1],
        "created_by": 1,
        "embargo_date": "2120-10-06",
        "contact": "foo@example.com",
        "access_right": "open"
    }
    assert valid_full == AccessSchemaV1().load(valid_full)


def test_invalid_access_right(vocabulary_clear):
    invalid_access_right = {
        "metadata_restricted": False,
        "files_restricted": False,
        "owners": [1],
        "created_by": 1,
        "access_right": "invalid value"
    }

    assert_raises_messages(
        lambda: AccessSchemaV1().load(invalid_access_right),
        {
            "access_right": [_(
                "Invalid value. Choose one of ['closed', 'embargoed', "
                "'open', 'restricted']."
            )]
        }
    )


# TODO: Implement
# Tests not implemented in the interest of time
@pytest.mark.skip()
def test_invalid_empty_owners(vocabulary_clear):
    assert False
