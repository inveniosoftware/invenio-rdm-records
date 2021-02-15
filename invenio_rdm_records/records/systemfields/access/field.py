# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Access system field."""

from invenio_records.systemfields import SystemField

from .embargo import Embargo
from .grants import Grants
from .owners import Owners
from .protection import Protection


class Access:
    """Access management per record."""

    grant_cls = Grants
    owners_cls = Owners
    protection_cls = Protection
    embargo_cls = Embargo

    def __init__(
        self,
        owned_by=None,
        grants=None,
        protection=None,
        embargo=None,
        owners_cls=None,
        grants_cls=None,
        protection_cls=None,
    ):
        owners_cls = owners_cls or Access.owners_cls
        grants_cls = grants_cls or Access.grant_cls
        protection_cls = protection_cls or Access.protection_cls

        # since owned_by and grants are basically sets and empty sets
        # evaluate to False, assigning 'self.x = x or x_cls()' could lead to
        # unwanted results
        self._owned_by = owned_by
        if owned_by is None:
            self._owned_by = owners_cls()

        self._grants = grants
        if grants is None:
            self._grants = grants_cls()

        self._protection = protection
        if protection is None:
            self._protection = protection_cls("public", "public")

        self._embargo = embargo

    @property
    def owned_by(self):
        """The set of owners for the record."""
        return self._owned_by

    @property
    def owners(self):
        """An alias for the owned_by property."""
        return self.owned_by

    @property
    def grants(self):
        """The set of permission grants for the record."""
        return self._grants

    @property
    def protection(self):
        """The file & record protection level of the record."""
        return self._protection

    @property
    def embargo(self):
        """The embargo information of the record."""
        return self._embargo

    def dump(self):
        """Dump the field values as dictionary."""
        access = {
            "record": self.protection.record,
            "files": self.protection.files,
            "owned_by": self.owned_by.dump(),
            "grants": self.grants.dump(),
        }

        if self.embargo is not None:
            access["embargo"] = self.embargo.dump()

        return access

    @classmethod
    def from_dict(
        cls,
        access_dict,
        grants_cls=None,
        owners_cls=None,
        protection_cls=None,
        embargo_cls=None,
    ):
        """Create a new Access object from the specified 'access' property."""
        grants_cls = grants_cls or Access.grant_cls
        owners_cls = owners_cls or Access.owners_cls
        protection_cls = protection_cls or Access.protection_cls
        embargo_cls = embargo_cls or Access.embargo_cls

        if access_dict:
            owners = owners_cls()
            grants = grants_cls()

            for owner_dict in access_dict.get("owned_by", []):
                owners.add(owners_cls.owner_from_dict(owner_dict))

            for grant_dict in access_dict.get("grants", []):
                grants.add(grants.grant_cls.from_dict(grant_dict))

            protection = protection_cls(
                access_dict["record"], access_dict["files"]
            )

            embargo = None
            embargo_dict = access_dict.get("embargo")
            if embargo_dict is not None:
                embargo = embargo_cls.from_dict(embargo_dict)

        else:
            # if there is no 'access' property, fall back to default values
            owners = owners_cls()
            grants = grants_cls()
            protection = protection_cls()
            embargo = None

        return cls(
            owned_by=owners,
            grants=grants,
            protection=protection,
            embargo=embargo,
        )

    def __repr__(self):
        protection_str = "{}/{}".format(
            self.protection.record, self.protection.files
        )
        if self.embargo is not None:
            embargo_str = "embargo: {}".format(repr(self.embargo))
        else:
            embargo_str = "no embargo"

        return "<{} (protection: {}, {}, owners: {}, grants: {})>".format(
            type(self).__name__,
            protection_str,
            embargo_str,
            len(self.owners),
            len(self.grants),
        )


class AccessField(SystemField):
    """System field for managing record access."""

    def __init__(self, key="access", access_obj_class=Access):
        self._access_obj_class = access_obj_class
        super().__init__(key=key)

    def obj(self, instance):
        """Get the access object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._access_obj_class.from_dict(data)
            self._set_cache(instance, obj)
            return obj

        return None

    def __get__(self, record, owner=None):
        if record is None:
            # access by class
            return self

        # access by object
        return self.obj(record)

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        record["access"] = self.obj(record).dump()
