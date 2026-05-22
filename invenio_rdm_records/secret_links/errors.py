# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Errors for secret links."""

from invenio_i18n import gettext as _


class SecretLinkError(Exception):
    """Base exception for secret links errors."""

    pass


class InvalidPermissionLevelError(SecretLinkError):
    """An invalid permission level."""

    def __init__(self, permission_level):
        """Initialise error."""
        super().__init__(
            _(
                "Invalid permission level: %(permission_level)s",
                permission_level=permission_level,
            )
        )
