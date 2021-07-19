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

    def __init__(self, until=None, reason=None, active=None):
        """Create a new Embargo."""
        self.until = until
        if isinstance(until, str):
            self.until = arrow.get(until).datetime

        self.reason = reason
        self._active = active

    @property
    def active(self):
        """Whether or not the Embargo is (still) active."""
        if self._active is not None:
            return self._active

        elif self.until is None:
            return False

        return arrow.utcnow().datetime < self.until

    @active.setter
    def active(self, value):
        """Set the Embargo's (boolean) active state."""
        self._active = bool(value)

    def _lift(self):
        """Internal method to lift the embargo.

        Returns ``True`` if the embargo was actually lifted (i.e. it was
        expired but still marked as active).
        """
        if self.until is not None:
            if arrow.utcnow().datetime > self.until:
                was_active = bool(self._active)
                self.active = False
                return was_active

        return False

    def clear(self):
        """Clear any information if the embargo was ever active."""
        self.until = None
        self.reason = None
        self._active = None

    def dump(self):
        """Dump the embargo as dictionary."""
        until_str = None
        if self.until is not None:
            until_str = self.until.strftime("%Y-%m-%d")

        return {
            "active": self.active,
            "until": until_str,
            "reason": self.reason,
        }

    def __repr__(self):
        """Return repr(self)."""
        if self == Embargo():
            return "<No Embargo>"

        until_str = self.until or "n/a"

        return "<{} (active: {}, until: {}, reason: {})>".format(
            type(self).__name__, self.active, until_str, self.reason
        )

    def __eq__(self, other):
        """Return self == other."""
        if type(self) != type(other):
            return False

        return (
            self.reason == other.reason
            and self.until == other.until
            and self.active == other.active
        )

    def __ne__(self, other):
        """Return self != other."""
        return not (self == other)

    def __bool__(self):
        """Return bool(self)."""
        return self.active

    @classmethod
    def from_dict(cls, dict_, ignore_active_value=False):
        """Parse the Embargo from the given dictionary."""
        if not dict_:
            return cls()

        until = dict_.get("until")
        if until:
            until = arrow.get(until).datetime

        reason = dict_.get("reason")
        active = dict_.get("active")
        if ignore_active_value:
            # with ignore_active_value, the 'active' value is re-calculated
            # instead of parsed
            active = None

        if not until and not reason and not active:
            return cls()

        return cls(until=until, reason=reason, active=active)
