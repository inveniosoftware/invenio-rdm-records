# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""Secret links for sharing access to records."""

from .models import SecretLink, SecretLinkSerializer
from .permissions import LinkNeed

__all__ = ("LinkNeed", "SecretLink", "SecretLinkSerializer")
