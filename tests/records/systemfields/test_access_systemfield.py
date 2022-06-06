# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test access system field."""

from base64 import b64encode
from datetime import timedelta

import arrow
import pytest

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.systemfields.access import (
    Embargo,
    Grant,
    Grants,
    Owner,
    Owners,
    Protection,
    RecordAccess,
)

#
# Protection
#


def test_protection_valid():
    p = Protection("public", "public")
    assert p.record == "public"
    assert p.files == "public"
    p.set("restricted", files="restricted")
    assert p.record == "restricted"
    assert p.files == "restricted"


def test_protection_invalid_values():
    with pytest.raises(ValueError):
        Protection("invalid", "values")


#
# Embargo
#


def test_embargo_creation():
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    embargo = Embargo(until=next_year, reason="espionage")
    assert embargo.active

    last_year = arrow.utcnow().datetime + timedelta(days=-365)
    embargo = Embargo(until=last_year, reason="espionage")
    assert not embargo.active


def test_embargo_from_dict():
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    embargo_dict = {"until": next_year, "active": True, "reason": "espionage"}
    embargo = Embargo.from_dict(embargo_dict)
    assert embargo.active
    assert embargo.until == next_year
    assert embargo.reason == "espionage"
    embargo_dict["until"] = next_year.strftime("%Y-%m-%d")
    assert embargo.dump() == embargo_dict


def test_embargo_lift():
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    last_year = arrow.utcnow().datetime + timedelta(days=-365)
    embargo_dict1 = {"until": next_year, "active": True, "reason": "espionage"}
    embargo_dict2 = {"until": last_year, "active": True, "reason": "espionage"}
    new_embargo = Embargo.from_dict(embargo_dict1)
    old_embargo = Embargo.from_dict(embargo_dict2)

    assert old_embargo._lift()
    assert not old_embargo.active
    assert not new_embargo._lift()
    assert new_embargo.active


#
# Grants
#


def test_grant_creation(users, roles):
    user = users[0]
    role = roles[0]
    grant = Grant(user, "view")
    assert grant.subject_type == "user"
    assert grant.subject_id == user.id
    assert grant.subject == user

    grant = Grant(role, "view")
    assert grant.subject_type == "role"
    assert grant.subject_id == role.id
    assert grant.subject == role

    grant = Grant(None, "view", subject_type="sysrole", subject_id="system")
    assert grant.subject_type == "sysrole"
    assert grant.subject_id == "system"
    assert grant.subject is None


def test_grant_from_dict(users):
    user = users[0]
    grant_dict = {"subject": "user", "id": user.id, "level": "view"}
    grant = Grant.from_dict(grant_dict)
    assert grant.subject_type == "user"
    assert grant.subject_id == user.id
    assert grant.subject == user


def test_grant_to_need(users, roles):
    user = users[0]
    role = roles[0]
    grant = Grant(user, "view")
    need = grant.to_need()
    assert need.method == "id"
    assert need.value == user.id

    grant = Grant(role, "view")
    need = grant.to_need()
    assert need.method == "role"
    assert need.value == role.name

    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    grant = Grant.from_dict(dict_)
    need = grant.to_need()
    assert need.method == "system_role"
    assert need.value == "system"


def test_grant_to_token():
    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    grant = Grant.from_dict(dict_)
    token = "{}.{}.{}".format(
        b64encode("sysrole".encode()).decode(),
        b64encode("system".encode()).decode(),
        b64encode("view".encode()).decode(),
    )
    assert grant.to_token() == token


def test_grant_from_token():
    token = "{}.{}.{}".format(
        b64encode("sysrole".encode()).decode(),
        b64encode("system".encode()).decode(),
        b64encode("view".encode()).decode(),
    )
    grant = Grant.from_token(token)
    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    assert grant.to_dict() == dict_


def test_grant_to_and_from_token():
    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    grant = Grant.from_dict(dict_)
    assert Grant.from_token(grant.to_token()) == grant


def test_grants_creation(users, roles):
    user = users[0]
    role = roles[0]
    grant1 = Grant(user, "manage")
    grant2 = Grant(role, "view")
    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    grant3 = Grant.from_dict(dict_)

    grants = Grants([grant1, grant2, grant3, grant1])
    assert len(grants) == 3

    grants.add(grant2)
    assert len(grants) == 3


def test_grants_dump(users, roles):
    user = users[0]
    role = roles[0]
    grant1 = Grant(user, "manage")
    grant2 = Grant(role, "view")
    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    grant3 = Grant.from_dict(dict_)
    grants = Grants([grant1, grant2, grant3])

    dump = grants.dump()
    assert len(dump) == 3
    assert grant1.to_dict() in dump
    assert grant2.to_dict() in dump
    assert grant3.to_dict() in dump


def test_grants_needs(users, roles):
    user = users[0]
    role = roles[0]
    grant1 = Grant(user, "manage")
    grant2 = Grant(role, "view")
    dict_ = {"subject": "sysrole", "id": "system", "level": "view"}
    grant3 = Grant.from_dict(dict_)
    grants = Grants([grant1, grant2, grant3])

    assert len(grants.needs("view")) == 3
    # TODO check for higher permissions as well, once the permission
    #      hierarchy is in place


#
# Owners
#


def test_owner_creation(users):
    user = users[0]
    owner1 = Owner({"user": user.id})
    owner2 = Owner(user)
    assert owner1.owner_id == owner2.owner_id == user.id
    assert owner1.owner_type == owner2.owner_type == "user"
    assert owner1.dump() == owner2.dump()


def test_owner_resolve(users):
    user = users[0]
    owner = Owner({"user": user.id})
    assert owner.resolve() == user


def test_owner_resolve_invalid():
    owner = Owner({"user": -1})
    with pytest.raises(LookupError):
        assert owner.resolve(raise_exc=True)


def test_owner_dump():
    dict_ = {"user": 1}
    owner = Owner(dict_)
    assert owner.dump() == dict_


def test_owners_creation(users):
    user = users[0]
    owner1 = Owner({"user": user.id})
    owner2 = Owner(user)
    owner3 = Owner({"user": 1337})
    owners = Owners([owner1, owner2, owner1])
    assert len(owners) == 1
    owners.add(owner3)
    assert len(owners) == 2
    owners.add(owner3)
    assert len(owners) == 2
    owners.add(user)
    assert len(owners) == 2


#
# Record Access System Field
#


def test_access_field_on_record(running_app, minimal_record, parent, users):
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    minimal_record["access"]["embargo"] = {
        "until": next_year.strftime("%Y-%m-%d"),
        "active": True,
        "reason": "nothing in particular",
    }
    rec = RDMRecord.create(minimal_record, parent=parent)

    assert isinstance(rec.access, RecordAccess)
    assert isinstance(rec.access.protection, Protection)
    assert rec.access.protection.record == minimal_record["access"]["record"]
    assert rec.access.protection.files == minimal_record["access"]["files"]
    assert isinstance(rec.access.embargo, Embargo)


def test_access_field_update_embargo(running_app, minimal_record, parent, users):
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    minimal_record["access"]["embargo"] = {
        "until": next_year.strftime("%Y-%m-%d"),
        "active": True,
        "reason": "nothing in particular",
    }
    rec = RDMRecord.create(minimal_record.copy(), parent=parent)
    assert rec.access.embargo

    rec.access.embargo.active = False
    rec.access.embargo.reason = "can't remember"
    rec.commit()

    minimal_record["access"]["embargo"]["active"] = False
    minimal_record["access"]["embargo"]["reason"] = "can't remember"


def test_access_field_clear_embargo(minimal_record, parent):
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    minimal_record["access"]["embargo"] = {
        "until": next_year.strftime("%Y-%m-%d"),
        "active": True,
        "reason": "nothing in particular",
    }
    rec = RDMRecord.create(minimal_record, parent=parent)

    rec.access.embargo.clear()
    assert not rec.access.embargo


def test_access_field_lift_embargo(minimal_record, parent):
    tomorrow = arrow.utcnow().datetime + timedelta(days=+1)
    minimal_record["access"]["record"] = "public"
    minimal_record["access"]["files"] = "restricted"
    minimal_record["access"]["embargo"] = {
        "until": tomorrow.strftime("%Y-%m-%d"),
        "active": True,
        "reason": "nothing in particular",
    }
    rec = RDMRecord.create(minimal_record, parent=parent)
    assert not rec.access.lift_embargo()
    assert rec["access"]["record"] == "public"
    assert rec["access"]["files"] == "restricted"
    assert rec["access"]["embargo"]["active"] is True

    today = arrow.utcnow().datetime
    rec.access.embargo.until = today
    assert rec.access.lift_embargo()
    assert rec.access.protection.record == "public"
    assert rec.access.protection.record == "public"
    assert rec.access.embargo.active is False


def test_access_field_update_protection(running_app, minimal_record, parent, users):
    minimal_record["access"]["record"] = "restricted"
    minimal_record["access"]["files"] = "restricted"

    rec = RDMRecord.create(minimal_record, parent=parent)
    assert rec.access.protection.record == "restricted"
    assert rec.access.protection.files == "restricted"

    rec.access.protection.set("public", "public")
    rec.commit()

    assert rec["access"]["record"] == "public"
    assert rec["access"]["files"] == "public"


#
# Parent Record Access System Field
#


def test_access_field_update_owners(running_app, minimal_record, parent, users):
    rec = RDMRecord.create(minimal_record.copy(), parent=parent)
    parent = rec.parent
    new_owner = {"user": 1337}
    parent.access.owners.add(users[0])
    parent.access.owners.add(new_owner)
    parent.commit()

    num_owners = len(parent.access.owners)
    assert num_owners == len(parent["access"]["owned_by"])
    assert num_owners == 2
    assert new_owner in parent["access"]["owned_by"]

    parent.access.owners.remove(new_owner)
    parent.commit()

    num_owners = len(parent.access.owners)
    assert num_owners == len(parent["access"]["owned_by"])
    assert num_owners == 1
    assert new_owner not in parent["access"]["owned_by"]
