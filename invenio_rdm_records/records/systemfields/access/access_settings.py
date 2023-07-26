# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Access settings field."""


class AccessSettings:
    """Access settings for a parent record."""

    def __init__(self, settings_dict):
        """Constructor."""
        self.allow_user_requests = settings_dict.get("allow_user_requests", False)
        self.allow_guest_requests = settings_dict.get("allow_guest_requests", False)
        self.accept_conditions_text = settings_dict.get("accept_conditions_text", None)

    def dump(self):
        """Dump the record as dictionary."""
        return {
            "allow_user_requests": self.allow_user_requests,
            "allow_guest_requests": self.allow_guest_requests,
            "accept_conditions_text": self.accept_conditions_text,
        }

    def __repr__(self):
        """Return repr(self)."""
        return "<{} requests: {}/{}, text: {}>".format(
            type(self).__name__,
            self.allow_guest_requests,
            self.allow_user_requests,
            self.accept_conditions_text,
        )
