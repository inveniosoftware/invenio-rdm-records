# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Embargo class for the access system field."""

import arrow


class Embargo:
    def __init__(self, until, reason=None, active=None):
        self.until = until
        if isinstance(self.until, str):
            self.until = arrow.get().datetime

        self.reason = reason
        self._active = active

    @property
    def active(self):
        if self._active is not None:
            return self._active

        return arrow.utcnow().datetime < self.until

    @active.setter
    def set_active(self, value):
        self._active = value

    def clear(self):
        # TODO
        pass

    def lift(self):
        # TODO
        pass

    def dump(self):
        """Dump the embargo as dictionary."""
        return {
            "active": self.active,
            "until": self.until.isoformat(),
            "reason": self.reason,
        }

    def __repr__(self):
        return "<{} (active: {}, until: {}, reason: {})>".format(
            type(self).__name__, self.active, self.until, self.reason
        )

    def __bool__(self):
        return self.active

    @classmethod
    def from_dict(cls, dict_, ignore_active_value=False):
        """Parse the Embargo from the ."""
        until = arrow.get(dict_["until"]).datetime
        reason = dict_.get("reason")
        active = dict_.get("active")
        if ignore_active_value:
            # with ignore_active_value, the 'active' value is re-calculated
            # instead of parsed
            active = None

        return cls(until, reason=reason, active=active)
