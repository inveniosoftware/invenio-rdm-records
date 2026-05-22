# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Fixtures for metadata tests."""

from copy import deepcopy

import pytest


@pytest.fixture(scope="function")
def full_metadata(full_record):
    """Fixture for full incoming valid metdata."""
    return full_record["metadata"]


@pytest.fixture(scope="function")
def minimal_metadata(minimal_record):
    """Fixture for minimal incoming valid metdata."""
    return minimal_record["metadata"]


@pytest.fixture(scope="function")
def expected_minimal_metadata(minimal_metadata):
    """Fixture for minimal expected metdata."""
    expected_metadata = deepcopy(minimal_metadata)
    expected_metadata["creators"][0]["person_or_org"]["name"] = "Brown, Troy"
    return expected_metadata
