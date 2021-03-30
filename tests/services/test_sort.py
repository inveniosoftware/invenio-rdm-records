# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Sort tests."""


import pytest

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def service(app, location):
    """Service fixture."""
    return current_rdm_records.records_service


def test_sort_by_versions(
        service, superuser_identity, minimal_record):
    # Create version 1
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(draft.id, superuser_identity)

    # Create version 2
    draft = service.new_version(record.id, superuser_identity)
    # NOTE: needed because publication_date is stripped from draft
    service.update_draft(draft.id, superuser_identity, minimal_record)
    record_2 = service.publish(draft.id, superuser_identity)

    # Create version 3
    draft = service.new_version(record_2.id, superuser_identity)
    service.update_draft(draft.id, superuser_identity, minimal_record)
    record_3 = service.publish(draft.id, superuser_identity)

    # NOTE: we swap version 2 and 3, so that "newest" order is different
    #       than "versions" order
    # Swap version 2 and 3: we have to reach all the way to DB model to do so
    record_2._record.model.index = 3
    record_3._record.model.index = 2

    # Re-index them
    service.indexer.index(record_2._record)
    service.indexer.index(record_3._record)
    record_2._record.index.refresh()

    result = service.search(superuser_identity, sort='version',
                            params={"allversions": True}).to_dict()

    expected_order = [record_2.id, record_3.id, record.id]
    assert expected_order == [h["id"] for h in result['hits']['hits']]
