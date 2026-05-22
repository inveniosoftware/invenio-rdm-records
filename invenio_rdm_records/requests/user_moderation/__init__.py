# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""User moderation actions specific to RDM-Records."""

from .actions import on_approve, on_block, on_restore

__all__ = ("on_approve", "on_block", "on_restore")
