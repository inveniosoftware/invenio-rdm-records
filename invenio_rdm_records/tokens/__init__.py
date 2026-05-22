# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Resource access token for sharing access to resources of records."""

from .permissions import RATNeed
from .resource_access import validate_rat

__all__ = ("RATNeed", "validate_rat")
