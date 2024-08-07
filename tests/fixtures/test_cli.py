# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021-2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the CLI."""

from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_communities.members import Member
from invenio_requests import current_requests_service
from invenio_requests.records import Request

from invenio_rdm_records.cli import (
    create_records_custom_field,
    custom_field_exists_in_records,
)
from invenio_rdm_records.fixtures.demo import create_fake_community, create_fake_record
from invenio_rdm_records.fixtures.tasks import (
    create_demo_community,
    create_demo_inclusion_requests,
    create_demo_invitation_requests,
    create_demo_record,
    get_authenticated_identity,
)
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.requests import CommunitySubmission


def test_create_fake_demo_draft_record(
    app, location, db, search_clear, vocabularies, users
):
    """Assert that demo record creation works without failing."""
    user_id = users[0].id

    create_demo_record(user_id, create_fake_record(), publish=False)
    RDMDraft.index.refresh()

    user_identity = get_authenticated_identity(user_id)
    drafts = current_rdm_records_service.search_drafts(
        user_identity, is_published=False, q="versions.index:1"
    )
    assert drafts.total > 0

    create_demo_record(user_id, create_fake_record(), publish=True)
    RDMRecord.index.refresh()

    records = current_rdm_records_service.search(user_identity)
    assert records.total > 0


def test_create_fake_demo_communities(
    app, location, db, search_clear, vocabularies, users
):
    """Assert that demo communities creation works without failing."""
    user_id = users[0].id

    create_demo_community(user_id, create_fake_community())
    Community.index.refresh()

    user_identity = get_authenticated_identity(user_id)
    communities = current_communities.service.search(user_identity)
    assert communities.total > 0


def test_create_fake_demo_inclusion_requests(
    app, location, db, search_clear, vocabularies, users
):
    """Assert that demo inclusion requests creation works without failing."""
    user_id = users[0].id

    create_demo_record(user_id, create_fake_record(), publish=False)
    RDMDraft.index.refresh()
    create_demo_community(user_id, create_fake_community())
    Community.index.refresh()

    create_demo_inclusion_requests(user_id, 1)
    Request.index.refresh()

    user_identity = get_authenticated_identity(user_id)
    _t = CommunitySubmission.type_id
    reqs = current_requests_service.search(user_identity, type=_t)
    assert reqs.total > 0


def test_create_fake_demo_invitation_requests(
    app, location, db, search_clear, vocabularies, users
):
    """Assert that demo invitation requests creation works without failing."""
    first_user_id = users[0].id

    create_demo_record(first_user_id, create_fake_record(), publish=True)
    RDMDraft.index.refresh()
    comm = create_demo_community(first_user_id, create_fake_community())
    Community.index.refresh()
    user_identity = get_authenticated_identity(first_user_id)
    communities = current_communities.service.search(user_identity)
    comm = communities.to_dict()["hits"]["hits"][0]

    other_user_id = users[1].id
    create_demo_invitation_requests(other_user_id, 1)
    Member.index.refresh()

    service = current_communities.service.members
    reqs = service.search_invitations(system_identity, comm["id"])
    assert reqs.total > 0


def test_create_records_custom_fields(app, location, db, search_clear, cli_runner):
    """Assert that custom fields mappings are created for records."""
    result = cli_runner(create_records_custom_field, "-f", "cern:myfield")
    assert result.exit_code == 0

    record_mapping_field = list(RDMRecord.index.get_mapping().values())[0]["mappings"][
        "properties"
    ]["custom_fields"]
    draft_mapping_field = list(RDMDraft.index.get_mapping().values())[0]["mappings"][
        "properties"
    ]["custom_fields"]
    expected_value = {
        "dynamic": "true",
        "properties": {
            "cern:myfield": {"type": "text", "fields": {"keyword": {"type": "keyword"}}}
        },
    }
    assert record_mapping_field == expected_value
    assert draft_mapping_field == expected_value

    # check for existence
    RDMRecord.index.refresh()
    RDMDraft.index.refresh()

    result = cli_runner(custom_field_exists_in_records, "-f", "cern:myfield")
    assert result.exit_code == 0
    assert "Field cern:myfield exists" in result.output

    result = cli_runner(custom_field_exists_in_records, "-f", "unknownfield")
    assert result.exit_code == 0
    assert "Field unknownfield does not exist" in result.output
