# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Fixtures for metadata tests."""

import pytest


@pytest.fixture(scope="function")
def minimal_metadata(minimal_record):
    """Fixture for minimal valid metdata."""
    return minimal_record["metadata"]
