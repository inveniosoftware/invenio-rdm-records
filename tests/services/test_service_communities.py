# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records.records_service


# TODO: add tests
