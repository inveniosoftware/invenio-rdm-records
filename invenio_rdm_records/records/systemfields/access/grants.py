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
from invenio_access.proxies import current_access
from invenio_accounts.models import Role, User
from invenio_accounts.proxies import current_datastore
from invenio_db import db


class Grant:
    """Grant for a specific permission level on a record."""

    def __init__(
        self, permission, origin, subject=None, subject_type=None, subject_id=None
    ):
        """Permission grant for a specific subject (e.g. a user).

        If the ``subject`` argument is specified, it will be used to determine the
        values for ``subject_type`` and ``subject_id`` automatically.
        In case they are still specified at the same time, their values will
        take precedence over the automatically determined values.

        The ``origin`` value is an optional string describing the origin of the token.
        For example, it could indicate that the grant was created manually by the
        record's owner via the API, or that it was automatically created by the system.
        It is purely informational and not included in equality checks or similar.

        :param permission: The granted permission level.
        :param origin: The origin of the grant.
        :param subject: The subject of the permission grant.
        :param subject_type: An override for the subject's type.
        :param subject_id: An override for the subject's ID.
        """
        self._subject_type = self._subject_id = self._subject = None

        if isinstance(subject, dict):
            subject_type = subject_type or subject.get("type")
            subject_id = subject_id or subject.get("id")
            subject = None

        elif subject is not None:
            self._subject = subject
            subject_type = self.subject_type
            subject_id = self.subject_id

        if subject_type is None or subject_id is None:
            raise ValueError("The subject of the Grant is not specified")

        self.permission = permission
        self.origin = origin
        self._subject = subject
        self._subject_type = subject_type
        self._subject_id = str(subject_id)

    @property
    def subject(self):
        """The entity that is subject to the Grant.

        Note: If the subject entity has not been cached yet, this operation
        will trigger a database query.
        """
        if self._subject is None:
            self._subject = self.resolve_subject()

            if self._subject is not None:
                if self._subject_type == "role":
                    # NOTE: `RoleNeed` objects work with their name rather than ID
                    #       c.f. `invenio_access.utils:get_identity`
                    self._subject_id = self._subject.name
                else:
                    self._subject_id = str(self._subject.id)

        return self._subject

    def resolve_subject(self):
        """Force resolving of the grant's subject.

        If the grant subject should be resolvable (i.e. it is not a system role) but
        cannot be found, a ``LookupError`` will be raised.
        """
        registered_system_roles = current_access.system_roles
        type_ = self._subject_type
        subject = None

        if type_ == "user":
            with db.session.no_autoflush:
                subject = current_datastore.get_user(self._subject_id)
        elif type_ == "role":
            subject = current_datastore.find_role(self._subject_id)

        # check if the subject could be resolved or is a registered system role
        if (type_ in ["user", "role"] and subject is None) or (
            type_ == "system_role" and self._subject_id not in registered_system_roles
        ):
            raise LookupError(f"Could not find grant subject: {self.to_dict()}")

        return subject

    @property
    def subject_type(self):
        """The type of the Grant's subject (user, role or system_role)."""
        if self._subject_type:
            return self._subject_type

        if isinstance(self.subject, User):
            return "user"

        elif isinstance(self.subject, Role):
            return "role"

        else:
            # if it's nothing else, it's gonna be a system role
            # (which doesn't have a persisted subject entity)
            return "system_role"

    @property
    def subject_id(self):
        """The ID of the Grant's subject."""
        if self._subject_id:
            return self._subject_id

        if self.subject_type == "role":
            return self.subject.name

        return self.subject.id

    def to_need(self):
        """Create the need that this grant provides.

        Note: This operation doesn't resolve the subject, and thus won't cause any
        database lookups even if the. On the flipside, it also won't check if the
        subject exists.
        """
        if self.subject_type == "user":
            # NOTE: the `UserNeed` must have an integer as ID, otherwise it won't match
            need = UserNeed(int(self.subject_id))

        elif self.subject_type == "role":
            # NOTE: according to `invenio_access.utils:get_identity`, RoleNeeds
            # take the roles' names
            need = RoleNeed(self.subject_id)

        elif self.subject_type == "system_role":
            # system roles don't have a model class behind them, so
            # it's probably best to go with the subject_id
            need = SystemRoleNeed(self.subject_id)

        return need

    def to_token(self):
        """Dump the Grant to a grant token."""
        # do something similar to JWT: base64-encode and separate with dots
        # this ensures that we can always separate the values again
        # (b/c the base64 alphabet doesn't contain the dot)
        return "{0}.{1}.{2}".format(
            b64encode(self.subject_type.encode(), b"-_").decode(),
            b64encode(self.subject_id.encode(), b"-_").decode(),
            b64encode(self.permission.encode(), b"-_").decode(),
        )

    def to_dict(self):
        """Dump the Grant to a dictionary."""
        return {
            "subject": {
                "id": self.subject_id,
                "type": self.subject_type,
            },
            "permission": self.permission,
            "origin": self.origin,
        }

    @classmethod
    def create(
        cls, subject_type, subject_id, permission, origin, resolve_subject=False
    ):
        """Create a Grant from the specified parts (all of which should be strings).

        :param subject_type: The grant subject's type (user, role or system_role).
        :param subject_id: The grant subject's ID.
        :param permission: The grant's permission level.
        :param origin: A string describing the origin of the grant token.
        :param resolve_subject: Whether to fetch the subject entity from the DB eagerly.
        """
        if subject_type not in ["user", "role", "system_role"]:
            raise ValueError(f"Unknown subject type: {subject_type}")

        grant = cls(
            permission=permission,
            origin=origin,
            subject=None,
            subject_type=subject_type,
            subject_id=subject_id,
        )

        if resolve_subject:
            # NOTE: accessing the `subject` property populates the cache as side effect
            grant.subject

        return grant

    @classmethod
    def from_token(cls, token):
        """Parse the grant token into a Grant."""
        subject_type, subject_id, permission = (
            b64decode(val, b"-_").decode() for val in token.split(".")
        )

        return cls.create(subject_type, subject_id, permission, origin=None)

    @classmethod
    def from_dict(cls, dict_):
        """Parse the dictionary into a Grant."""
        subject_type = dict_["subject"]["type"]
        subject_id = dict_["subject"]["id"]
        permission = dict_["permission"]
        origin = dict_.get("origin", None)

        return cls.create(subject_type, subject_id, permission, origin)

    def __hash__(self):
        """Return hash(self)."""
        return hash(self.subject_type) + hash(self.subject_id) + hash(self.permission)

    def __eq__(self, other):
        """Return self == other."""
        if type(self) != type(other):
            return False

        return (
            self.subject_type == other.subject_type
            and self.subject_id == other.subject_id
            and self.permission == other.permission
        )

    def __ne__(self, other):
        """Return self != other."""
        return not self == other

    def __repr__(self):
        """Return repr(self)."""
        return "<{0} (permission: {1}, subject: {{id: {2}, type: {3}}})>".format(
            type(self).__name__,
            self.permission,
            self.subject_id,
            self.subject_type,
        )


class Grants(list):
    """List of grants for various permission levels on a record."""

    grant_cls = Grant

    def __init__(self, grants=None):
        """Create a new list of Grants."""
        for grant in grants or []:
            self.add(grant)

    def append(self, grant):
        """Add the grant to the list of grants."""
        if grant not in self:
            super().append(grant)

    def add(self, grant):
        """Alias for self.append(grant)."""
        self.append(grant)

    def extend(self, grants):
        """Add all new items from the specified grants to this list."""
        for grant in grants:
            self.add(grant)

    def create(
        self,
        subject_type,
        subject_id,
        permission,
        origin,
        resolve_subject=False,
    ):
        """Create a new access grant and add it to the list of grants."""
        grant = Grant.create(
            subject_type=subject_type,
            subject_id=subject_id,
            permission=permission,
            origin=origin,
            resolve_subject=resolve_subject,
        )
        self.add(grant)
        return grant

    def needs(self, permission):
        """Get allowed needs for the given permission level."""
        return {grant.to_need() for grant in self if grant.permission == permission}

    def dump(self):
        """Dump the grants as a list of grant dictionaries."""
        return [grant.to_dict() for grant in self]
