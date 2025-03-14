# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Owners classes for the access system field."""

from invenio_access.permissions import system_user_id
from invenio_accounts.models import User
from invenio_db import db
from invenio_users_resources.services.schemas import SystemUserSchema


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

        elif owner is not None:
            raise TypeError("invalid owner type: {}".format(type(owner)))

    def dump(self):
        """Dump the owner to a dictionary."""
        if self.owner_type is None and self.owner_id is None:
            return None

        return {self.owner_type: self.owner_id}

    def resolve(self, raise_exc=False):
        """Resolve the owner entity (e.g. User) via a database query."""
        if self._entity is None:
            if self.owner_type is None and self.owner_id is None:
                return None

            elif self.owner_type == "user":
                if self.owner_id == system_user_id:
                    # system user
                    self._entity = SystemUserSchema().dump({})
                else:
                    # real user
                    self._entity = db.session.get(User, self.owner_id)

            else:
                raise ValueError("unknown owner type: {}".format(self.owner_type))

            if self._entity is None and raise_exc:
                raise LookupError("could not find owner: {}".format(self.dump()))

        return self._entity

    def __bool__(self):
        """Return bool(self)."""
        return self.owner_type is not None and self.owner_id is not None

    def __hash__(self):
        """Return hash(self)."""
        return hash(self.owner_type) + hash(self.owner_id)

    def __eq__(self, other):
        """Return self == other."""
        if type(self) != type(other):
            return False

        return self.owner_type == other.owner_type and self.owner_id == other.owner_id

    def __ne__(self, other):
        """Return self != other."""
        return not self == other

    def __str__(self):
        """Return str(self)."""
        return str(self.resolve())

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.resolve())
