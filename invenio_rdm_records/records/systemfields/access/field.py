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


class AccessField(SystemField):
    """Field for managing record access."""

    def __init__(
        self,
        key="access",
        owned_by=None,
        grants=None,
        protection=None,
        embargo=None,
        grants_cls=Grants,
        owners_cls=Owners,
        protection_cls=Protection,
        embargo_cls=Embargo,
    ):
        self._grants_cls = grants_cls
        self._owners_cls = owners_cls
        self._protection_cls = protection_cls
        self._embargo_cls = embargo_cls

        # since owned_by and grants are basically sets and empty sets
        # evaluate to False, assigning 'self.x = x or x_cls()' could lead to
        # unwanted results
        self._owned_by = owned_by
        if owned_by is None:
            self._owned_by = self._owners_cls()

        self._grants = grants
        if grants is None:
            self._grants = self._grants_cls()

        self._protection = protection
        if protection is None:
            self._protection = self._protection_cls("public", "public")

        self._embargo = embargo

        super().__init__(key=key)

    @property
    def owned_by(self):
        return self._owned_by

    @property
    def owners(self):
        """An alias for the owned_by property."""
        return self.owned_by

    @property
    def grants(self):
        return self._grants

    @property
    def protection(self):
        return self._protection

    @property
    def embargo(self):
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

    def __get__(self, record, owner=None):
        return self

    def post_init(self, record, data, model=None, **kwargs):
        """Initialize the field values after the record is initialized."""
        access_dict = data["access"]
        owners = self._owners_cls()
        grants = self._grants_cls()

        for owner_dict in access_dict.get("owned_by", []):
            owners.add(owners.owner_from_dict(owner_dict))

        for grant_dict in access_dict.get("grants", []):
            grants.add(grants.grant_cls.from_dict(grant_dict))

        protection = self._protection_cls(
            access_dict["record"], access_dict["files"]
        )

        embargo = None
        embargo_dict = access_dict.get("embargo")
        if embargo_dict is not None:
            embargo = self._embargo_cls.from_dict(embargo_dict)

        self.__init__(
            owned_by=owners,
            grants=grants,
            protection=protection,
            embargo=embargo,
            grants_cls=self._grants_cls,
            owners_cls=self._owners_cls,
            protection_cls=self._protection_cls,
            embargo_cls=self._embargo_cls,
        )

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        record["access"] = self.dump()
