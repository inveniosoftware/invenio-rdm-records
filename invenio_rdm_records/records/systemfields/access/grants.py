# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Grants classes for the access system field."""

from base64 import b64decode, b64encode

from flask_principal import RoleNeed, UserNeed
from invenio_access.permissions import SystemRoleNeed
from invenio_accounts.models import Role, User


class Grant:
    """Grant for a specific permission level on a record."""

    def __init__(
        self, subject, permission_level, subject_type=None, subject_id=None
    ):
        """Permission grant for a specific subject (e.g. a user).

        :param subject: The subject of the permission grant.
        :param permission_level: The granted permission level.
        """
        self.subject = subject
        self.permission_level = permission_level
        self._subject_type = subject_type
        self._subject_id = subject_id

    @property
    def subject_type(self):
        if self._subject_type:
            return self._subject_type

        if isinstance(self.subject, User):
            return "user"

        elif isinstance(self.subject, Role):
            return "role"

        else:
            # TODO
            raise NotImplementedError()

    @property
    def subject_id(self):
        if self._subject_id:
            return self._subject_id

        return self.subject.id

    def covers(self, permission):
        """Check if this Grant covers the specified permission."""
        # TODO check this via a permission hierarchy
        return True

    def to_need(self):
        """Create the need that this grant provides."""
        if self.subject_type == "user":
            need = UserNeed(self.subject.id)

        elif self.subject_type == "role":
            # according to invenio_access.utils:get_identity, RoleNeeds
            # take the roles' names
            need = RoleNeed(self.subject.name)

        elif self.subject_type == "sysrole":
            # system roles don't have a model class behind them, so
            # it's probably best to go with the subject_id
            need = SystemRoleNeed(self.subject_id)

        return need

    def to_token(self):
        """Dump the Grant to a grant token."""
        # TODO
        # do something similar to JWT: base64-encode and separate with dots
        # this ensures that we can always separate the values again
        # (b/c the base64 alphabet doesn't contain the dot)
        return "{}.{}.{}".format(
            b64encode(self.subject_type),
            b64encode(self.subject_id),
            b64encode(self.permission_level),
        )

    def to_dict(self):
        """Dump the Grant to a dictionary."""
        return {
            "subject": self.subject_type,
            "id": self.subject_id,
            "level": self.permission_level,
        }

    @classmethod
    def from_string_parts(cls, subject_type, subject_id, permission_level):
        """Create a Grant from the specified parts."""

        if subject_type == "user":
            subject = User.query.get(subject_id)

        elif subject_type == "role":
            subject = Role.query.get(subject_id)

        elif subject_type == "sysrole":
            # TODO
            raise NotImplementedError()

        else:
            raise ValueError("unknown subject type: {}".format(subject_type))

        return cls(
            subject=subject,
            permission_level=permission_level,
            subject_type=subject_type,
            subject_id=subject_id,
        )

    @classmethod
    def from_token(cls, token):
        """Parse the grant token into a Grant."""
        # TODO
        subject_type, subject_id, permission_level = (
            b64decode(val) for val in token.split(".")
        )

        return cls.from_string_parts(
            subject_type, subject_id, permission_level
        )

    @classmethod
    def from_dict(cls, dict_):
        """Parse the dictionary into a Grant."""
        subject_type = dict_["subject"]
        subject_id = dict_["id"]
        permission_level = dict_["level"]

        return cls.from_string_parts(
            subject_type, subject_id, permission_level
        )


class Grants(set):
    """Set of grants for various permission levels on a record."""

    grant_cls = Grant

    def __init__(self, grants=None):
        super().__init__(grants or [])

    def needs(self, permission):
        """Get allowed needs for the given permission level."""
        needs = {grant.to_need() for grant in self if grant.covers(permission)}

        return needs

    def dump(self):
        """Dump the grants as a list of grant dictionaries."""
        return [grant.to_dict() for grant in self]
