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
    """Embargo class for the access system field."""

    def __init__(self, until, reason=None, active=None):
        """Create a new Embargo."""
        self.until = until
        if isinstance(self.until, str):
            self.until = arrow.get().datetime

        self.reason = reason
        self._active = active

    @property
    def active(self):
        """Whether or not the Embargo is (still) active."""
        if self._active is not None:
            return self._active

        return arrow.utcnow().datetime < self.until

    @active.setter
    def set_active(self, value):
        """Set the Embargo's (boolean) active state."""
        self._active = value

    def clear(self):
        """Completely remove the embargo."""
        # TODO remove the embargo information entirely
        pass

    def lift(self):
        """Update the embargo active status if it has expired."""
        if arrow.utcnow().datetime < self.until:
            self.active = False

    def dump(self):
        """Dump the embargo as dictionary."""
        return {
            "active": self.active,
            "until": self.until.isoformat(),
            "reason": self.reason,
        }

    def __repr__(self):
        """Return repr(self)."""
        return "<{} (active: {}, until: {}, reason: {})>".format(
            type(self).__name__, self.active, self.until, self.reason
        )

    def __bool__(self):
        """Return bool(self)."""
        return self.active

    @classmethod
    def from_dict(cls, dict_, ignore_active_value=False):
        """Parse the Embargo from the given dictionary."""
        until = arrow.get(dict_["until"]).datetime
        reason = dict_.get("reason")
        active = dict_.get("active")
        if ignore_active_value:
            # with ignore_active_value, the 'active' value is re-calculated
            # instead of parsed
            active = None

        return cls(until, reason=reason, active=active)
