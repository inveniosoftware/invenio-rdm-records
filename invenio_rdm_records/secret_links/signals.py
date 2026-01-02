# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Secret link signals."""

from blinker import Namespace

_signals = Namespace()

link_created = _signals.signal("link-created")
"""Signal indicating that a secret link was created."""

link_revoked = _signals.signal("link-revoked")
"""Signal indicating that a secret link was revoked."""
