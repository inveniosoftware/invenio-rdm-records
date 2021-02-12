# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Grants classes for the access system field."""

from base64 import b64decode, b64encode

from invenio_accounts.models import User


class Grant:
    def __init__(
        self, subject, permission, subject_type=None, subject_id=None
    ):
        """Permission grant for a specific subject (e.g. a user).

        :param subject: The subject of the permission grant.
        :param permission: The given permission.
        """
        self.subject = subject
        self.permission = permission
        self._subject_type = subject_type
        self._subject_id = subject_id or self.subject.id

    @property
    def subject_type(self):
        if self._subject_type:
            return self._subject_type

        if isinstance(self.subject, User):
            return "user"
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
        # TODO
        pass

    def to_token(self):
        """Dump the Grant to a grant token."""
        # TODO
        # do something similar to JWT: base64-encode and separate with dots
        # this ensures that we can always separate the values again
        # (b/c the base64 alphabet doesn't contain the dot)
        return "{}.{}.{}".format(
            b64encode(self.subject_type),
            b64encode(self.subject_id),
            b64encode(self.permission),
        )

    def to_dict(self):
        """Dump the Grant to a dictionary."""
        return {
            "subject": self.subject_type,
            "id": self.subject_id,
            "permission": self.permission,
        }

    @classmethod
    def from_token(cls, token):
        """Parse the grant token into a Grant."""
        # TODO
        subject_type, subject_id, permission = (
            b64decode(val) for val in token.split(".")
        )

        return cls(
            None,
            permission=permission,
            subject_type=subject_type,
            subject_id=subject_id,
        )

    @classmethod
    def from_dict(cls, dict_):
        """Parse the dictionary into a Grant."""
        subject_type = dict_["subject"]
        subject_id = dict_["id"]
        permission = dict_["level"]

        # TODO
        if subject_type == "user":
            subject = User.query.get(int(subject_id))
        elif subject_type == "role":
            raise NotImplementedError()
        elif subject_type == "sysrole":
            raise NotImplementedError()

        return cls(
            subject,
            permission,
            subject_type=subject_type,
            subject_id=subject_id,
        )


class Grants(set):
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
