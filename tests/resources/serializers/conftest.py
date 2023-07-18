# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
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
                "identifier": "10.5281/inveniordm.1234.parent",
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
def minimal_record(minimal_record, parent_record):
    """Minimal record metadata with added parent metadata."""
    minimal_record["parent"] = parent_record
    return minimal_record


@pytest.fixture
def enhanced_full_record(enhanced_full_record, parent_record):
    """Enhanced full record metadata with added parent metadata."""
    enhanced_full_record["parent"] = parent_record
    return enhanced_full_record
