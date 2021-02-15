# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Owners classes for the access system field."""

from invenio_accounts.models import User


class Owner:
    """An abstraction between owner entities and specifications as dicts."""

    def __init__(self, owner):
        """Create an owner from either a dictionary or a User."""
        self._entity = None
        self.owner_type = None
        self.owner_id = None

        if isinstance(owner, dict):
            if "user" in owner:
                self.owner_type = "user"
                self.owner_id = owner["user"]

            else:
                raise ValueError("unknown owner type: {}".format(owner))

        elif isinstance(owner, User):
            self._entity = owner
            self.owner_id = owner.id
            self.owner_type = "user"

        else:
            raise TypeError("invalid owner type: {}".format(type(owner)))

    def dump(self):
        """Dump the owner to a dictionary."""
        return {self.owner_type: self.owner_id}

    def resolve(self):
        """Resolve the owner entity (e.g. User) via a database query."""
        if self._entity is None:
            if self.owner_type == "user":
                self._entity = User.query.get(self.owner_id)

            else:
                raise ValueError(
                    "unknown owner type: {}".format(self.owner_type)
                )

        return self._entity

    def __str__(self):
        """Return str(self)."""
        return str(self.resolve())

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.resolve())


class Owners(set):
    """A set of owners for a record."""

    owner_cls = Owner

    def __init__(self, owners=None, owner_cls=None):
        """Create a new set of owners."""
        self.owner_cls = owner_cls or Owners.owner_cls
        for owner in owners or []:
            self.add(owner)

    def add(self, owner):
        """Add the specified owner to the set of owners.

        :param owner: The record's owner (either a dict, User or Owner).
        """
        if not isinstance(owner, self.owner_cls):
            owner = self.owner_cls(owner)

        super().add(owner)

    def dump(self):
        """Dump the owners as a list of owner dictionaries."""
        return [owner.dump() for owner in self]

    @classmethod
    def owner_from_dict(cls, dict_):
        """Parse the owned_by entry into a new Owners element."""
        if "user" in dict_:
            return User.query.get(dict_["user"])
        else:
            raise ValueError("unknown owner type: {}".format(dict_))
