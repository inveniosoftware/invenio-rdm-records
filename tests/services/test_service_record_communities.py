# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test community records service."""

import pytest
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records.components import ServiceComponent

from invenio_rdm_records.proxies import (
    current_rdm_records_service,
    current_record_communities_service,
)


def test_bulk_add_non_authorized_permission(community, uploader, record_factory):
    """Test adding multiple records from a non-authorized user."""
    record = record_factory.create_record(uploader=uploader, community=None)

    with pytest.raises(PermissionDeniedError):
        current_record_communities_service.bulk_add(
            uploader.identity, str(community.id), [record["id"]]
        )


def test_bulk_add_by_system_permission(community, community_owner, record_factory):
    """Test bulk add by system."""
    record = record_factory.create_record(uploader=community_owner, community=None)

    current_record_communities_service.bulk_add(
        system_identity, str(community.id), [record["id"]]
    )

    _rec = current_rdm_records_service.record_cls.pid.resolve(record["id"])
    assert community.id in _rec.parent.communities.ids


def test_bulk_add(community, uploader, record_factory):
    """Test bulk add functionality."""
    TOTAL_RECS = 3
    recs = [
        record_factory.create_record(uploader=uploader, community=None)
        for _ in range(TOTAL_RECS)
    ]

    current_record_communities_service.bulk_add(
        system_identity, str(community.id), [rec["id"] for rec in recs]
    )
    for rec in recs:
        _rec = current_rdm_records_service.record_cls.pid.resolve(rec["id"])
        assert community.id in _rec.parent.communities.ids


def test_bulk_add_already_in_community(community, uploader, record_factory):
    """Test failed addition when the record is already in the community."""
    record = record_factory.create_record(uploader=uploader, community=community)

    assert current_record_communities_service.bulk_add(
        system_identity, str(community.id), [record["id"]]
    ) == [
        {
            "record_id": record["id"],
            "community_id": str(community.id),
            "message": "Community already included.",
        }
    ]


def test_add_community_component_called(
    community, uploader, community_owner, record_factory, set_app_config_fn_scoped
):
    """The component `add_community` method is called and modifies the data."""

    class MockAddComponent(ServiceComponent):
        def add_community(self, identity, record, communities, **kwargs):
            communities.pop(-1)

    set_app_config_fn_scoped(
        {"RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS": [MockAddComponent]}
    )

    record = record_factory.create_record(uploader=community_owner, community=None)

    submitted_communities = [{"id": str(community.id)}, {"id": "dummy_id"}]
    requests, errors = current_record_communities_service.add(
        community_owner.identity,
        record["id"],
        {"communities": submitted_communities},
    )
    # check that the resulting requests did not include one for the dummy_id
    # which the component should have removed
    assert len(requests) == 1
    assert "dummy_id" not in [c["community_id"] for c in requests]


def test_remove_community_component_called(
    db, community, community2, uploader, record_factory, set_app_config_fn_scoped
):
    """The component `remove_community` method is called and blocks the removal."""
    test_community_id = community.id

    class MockRemoveComponent(ServiceComponent):
        def remove_community(
            self, identity, record, community, valid_data, errors, **kwargs
        ):
            if community["id"] == str(community2.id):
                current_app.logger.info(
                    f"Removing community {test_community_id} blocked by component"
                )
                raise PermissionDeniedError()

    set_app_config_fn_scoped(
        {"RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS": [MockRemoveComponent]}
    )

    record = record_factory.create_record(uploader=uploader, community=community)

    record.parent.communities.add(community2._record, default=False)
    record.parent.commit()
    db.session.commit()
    current_rdm_records_service.indexer.index(record, arguments={"refresh": True})

    requests, errors = current_record_communities_service.remove(
        system_identity,
        record["id"],
        {"communities": [{"id": str(test_community_id)}, {"id": str(community2.id)}]},
    )
    assert len(requests) == 1
    assert requests[0]["community"] == str(test_community_id)
    # The component should have blocked the removal of "dummy_id" and raised
    # PermissionDeniedError which should be caught and added to errors
    assert len(errors) == 1
    assert errors[0]["community"] == str(community2.id)
    assert "Permission denied" in errors[0]["message"]


def test_set_default_component_called(
    db, community, community2, uploader, record_factory, set_app_config_fn_scoped
):
    """The component `set_default` method is called and modifies the supplied arguments."""

    class MockSetDefaultComponent(ServiceComponent):
        def set_default(
            self, identity, record, default_community_id, valid_data, **kwargs
        ):
            record.parent.communities.default = community2.id

    set_app_config_fn_scoped(
        {"RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS": [MockSetDefaultComponent]}
    )

    record = record_factory.create_record(uploader=uploader, community=community)

    # add the record to the second community
    record.parent.communities.add(community2._record, default=False)
    record.parent.commit()
    db.session.commit()
    current_rdm_records_service.indexer.index(record, arguments={"refresh": True})

    current_record_communities_service.set_default(
        system_identity,
        record["id"],
        {"default": str(community.id)},
    )

    result = current_rdm_records_service.record_cls.pid.resolve(record["id"])
    assert str(result.parent.communities.default.id) == str(community2.id)


def test_bulk_add_component_called(
    community, uploader, record_factory, set_app_config_fn_scoped
):
    """The component `bulk_add` method is called and modifies the supplied arguments."""

    class MockBulkAddComponent(ServiceComponent):
        def bulk_add(self, identity, community_id, record_ids, set_default, **kwargs):
            record_ids.pop(-1)
            set_default["value"] = False

    set_app_config_fn_scoped(
        {"RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS": [MockBulkAddComponent]}
    )

    record = record_factory.create_record(uploader=uploader, community=None)
    record2 = record_factory.create_record(uploader=uploader, community=None)
    record3 = record_factory.create_record(uploader=uploader, community=None)

    errors = current_record_communities_service.bulk_add(
        system_identity,
        str(community.id),
        [record.pid.pid_value, record2.pid.pid_value, record3.pid.pid_value],
        set_default=False,
    )

    assert len(errors) == 0
    result1 = current_rdm_records_service.record_cls.pid.resolve(record.pid.pid_value)
    assert str(result1.parent.communities.default.id) == community.id
    assert community.id in result1.parent.communities.ids
    result2 = current_rdm_records_service.record_cls.pid.resolve(record2.pid.pid_value)
    assert str(result2.parent.communities.default.id) == community.id
    assert community.id in result2.parent.communities.ids
    result3 = current_rdm_records_service.record_cls.pid.resolve(record3.pid.pid_value)
    assert community.id not in result3.parent.communities.ids
    assert result3.parent.communities.default is None
