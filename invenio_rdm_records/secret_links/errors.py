# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Errors for secret links."""


class SecretLinkError(Exception):
    """Base exception for secret links errors."""

    pass


class InvalidPermissionLevelError(SecretLinkError):
    """An invalid permission level."""

    def __init__(self, permission_level):
        """Initialise error."""
        super().__init__(f"Invalid permission level: {permission_level}")
