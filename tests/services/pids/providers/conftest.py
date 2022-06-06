# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture(scope="function")
def record(app, location, db, superuser_identity, minimal_record):
    """Application factory fixture."""
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    record_ = service.publish(draft.id, superuser_identity)

    return record_
