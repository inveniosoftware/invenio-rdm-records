# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Owners classes for the access system field."""

from invenio_accounts.models import User


class Owners(set):
    def __init__(self, owners=None):
        super().__init__(owners or [])

    def dump(self):
        """Dump the owners as a list of owner dictionaries."""
        return [self.owner_to_dict(owner) for owner in self]

    @classmethod
    def owner_to_dict(cls, owner):
        """Dump the specified owner as a dictionary as expected in owned_by."""
        return {"user": owner.id}

    @classmethod
    def owner_from_dict(cls, dict_):
        """Parse the owned_by entry into a new Owners element."""
        if "user" in dict_:
            return User.query.get(dict_["user"])
        else:
            raise ValueError("unknown owner type: {}".format(dict_))
