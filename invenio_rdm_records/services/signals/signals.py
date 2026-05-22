# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Software Heritage signals."""

from blinker import Namespace

_signals = Namespace()

post_publish_signal = _signals.signal("record-post-publish")
"""Signal to be sent after a record is published."""
