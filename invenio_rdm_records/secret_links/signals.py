# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""Secret link signals."""

from blinker import Namespace

_signals = Namespace()

link_created = _signals.signal("link-created")
"""Signal indicating that a secret link was created."""

link_revoked = _signals.signal("link-revoked")
"""Signal indicating that a secret link was revoked."""
