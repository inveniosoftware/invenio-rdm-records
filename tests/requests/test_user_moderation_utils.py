# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.requests.user_moderation.utils import get_user_records_grouped


def test_get_user_records_grouped(
    running_app, verified_user, search_clear, minimal_record
):
    """Should return ordered lists by versions of records of a user."""
    identity = verified_user.identity

    # Record 1 (with 2 versions)
    draft = records_service.create(identity, minimal_record)
    record_v1 = records_service.publish(id_=draft.id, identity=identity)

    new_version = records_service.new_version(identity, id_=record_v1.id)
    records_service.update_draft(identity, new_version.id, minimal_record)
    record_v2 = records_service.publish(id_=new_version.id, identity=identity)

    new_version = records_service.new_version(identity, id_=record_v2.id)
    records_service.update_draft(identity, new_version.id, minimal_record)
    record_v3 = records_service.publish(id_=new_version.id, identity=identity)

    # Record 2: single version
    draft_2 = records_service.create(identity, minimal_record)
    record_2_v1 = records_service.publish(id_=draft_2.id, identity=identity)

    records_service.indexer.process_bulk_queue()
    records_service.record_cls.index.refresh()

    groups = get_user_records_grouped(verified_user.id)

    assert len(groups) == 2

    record_1_group = next(g for g in groups if record_v1.id in g)
    record_2_group = next(g for g in groups if record_2_v1.id in g)

    assert record_1_group == [record_v3.id, record_v2.id, record_v1.id]
    assert record_2_group == [record_2_v1.id]
