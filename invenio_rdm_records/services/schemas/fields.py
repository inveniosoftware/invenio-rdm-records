# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow field definitions."""

from flask import current_app
from marshmallow_utils.fields import SanitizedHTML as SanitizedHTMLBase


class SanitizedHTML(SanitizedHTMLBase):
    """String field that sanitizes HTML tags with the ``bleach`` library.

    In contrast to the base class, this field takes the Flask application's
    configuration into account.
    """

    @property
    def tags(self):
        """Get the list of allowed HTML tags.

        If no application context is available, use the field's set value as fallback.
        """
        try:
            return current_app.config["ALLOWED_HTML_TAGS"]
        except RuntimeError:
            return self._tags

    @tags.setter
    def tags(self, value):
        """Set the field's fallback value for allowed HTML tags."""
        self._tags = value

    @property
    def attrs(self):
        """Get the dictionary for allowed attributes per HTML tag.

        If no application context is available, use the field's set value as fallback.
        """
        try:
            return current_app.config["ALLOWED_HTML_ATTRS"]
        except RuntimeError:
            return self._attrs

    @attrs.setter
    def attrs(self, value):
        """Set the field's fallback value for allowed HTML attributes."""
        self._attrs = value
