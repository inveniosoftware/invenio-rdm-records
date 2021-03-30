# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Permissions for Invenio RDM Records."""

from flask_principal import RoleNeed, UserNeed
from invenio_access.permissions import any_user, authenticated_user, \
    system_process
from invenio_drafts_resources.services.records.permissions import \
    RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, Disable, SystemProcess

from invenio_rdm_records.records import RDMParent, RDMRecord
from invenio_rdm_records.services.generators import IfRestricted, RecordOwners


class TestRDMPermissionPolicy(RecordPermissionPolicy):
    """Define permission policies for RDM Records."""
    can_search = [AnyUser(), SystemProcess()]
    can_create = [AuthenticatedUser(), SystemProcess()]
    can_update = [Disable()]
    can_delete = [Disable()]
    can_read = [
        IfRestricted('record',
                     then_=[RecordOwners()],
                     else_=[AnyUser(), SystemProcess()])
                     ]
    can_read_files = [
        IfRestricted('files',
                     then_=[RecordOwners()],
                     else_=[AnyUser(), SystemProcess()])
                     ]
    can_update_files = [Disable()]
    can_read_draft = [RecordOwners()]
    can_update_draft = [RecordOwners()]
    can_delete_draft = [RecordOwners()]
    can_read_draft_files = [RecordOwners()]
    can_read_update_files = [RecordOwners()]
    can_publish = [RecordOwners()]
    can_manage = [RecordOwners()]


def test_permission_policy_generators(app, anyuser_identity,
                                      authenticated_identity,
                                      superuser_identity,
                                      system_process_identity):
    """Test permission policies with given Identities."""
    policy = TestRDMPermissionPolicy

    # TODO: add to fixture
    rest_record = RDMRecord.create({}, access={}, parent=RDMParent.create({}))
    rest_record.access.protection.set("restricted", "restricted")
    rest_record.parent.access.owners.add({'user': 1})

    # TODO: add to fixture
    pub_record = RDMRecord.create({}, access={}, parent=RDMParent.create({}))
    pub_record.access.protection.set("public", "public")
    pub_record.parent.access.owners.add({'user': 21})

    assert policy(action='search').allows(anyuser_identity)
    assert policy(action='search').allows(system_process_identity)
    assert policy(action='create').allows(authenticated_identity)
    assert policy(action='create').allows(system_process_identity)
    assert isinstance(policy(action='update').generators[0], Disable)
    assert isinstance(policy(action='delete').generators[0], Disable)
    assert policy(action='read'
                  ).generators[0].needs(
                      record=rest_record) == {UserNeed(1)}
    assert policy(action='read'
                  ).generators[0].needs(
                      record=pub_record) == {system_process, any_user}
    assert policy(action='read_files'
                  ).generators[0].needs(
                      record=rest_record) == {UserNeed(1)}
    assert isinstance(policy(action='update_files').generators[0], Disable)
    assert policy(action='read_draft'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]
    assert policy(action='update_draft'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]
    assert policy(action='delete_draft'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]
    assert policy(action='read_draft_files'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]
    assert policy(action='read_update_files'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]
    assert policy(action='publish'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]
    assert policy(action='manage'
                  ).generators[0].needs(
                      record=rest_record) == [UserNeed(1)]


def test_permission_policy_needs_excludes(superuser_role_need):
    """Test permission policy excluding 'superuser_role_need'."""
    search_perm = TestRDMPermissionPolicy(action='search')
    create_perm = TestRDMPermissionPolicy(action='create')
    update_perm = TestRDMPermissionPolicy(action='update')
    delete_perm = TestRDMPermissionPolicy(action='delete')
    updates_files_perm = TestRDMPermissionPolicy(action='updates_files')

    assert search_perm.needs == {superuser_role_need, any_user, system_process}
    assert search_perm.excludes == set()

    assert create_perm.needs == {superuser_role_need,
                                 authenticated_user, system_process}
    assert create_perm.excludes == set()

    assert update_perm.needs == {superuser_role_need}
    assert update_perm.excludes == {any_user}

    assert delete_perm.needs == {superuser_role_need}
    assert delete_perm.excludes == {any_user}

    assert updates_files_perm.needs == {superuser_role_need}
    assert updates_files_perm.excludes == {any_user}
