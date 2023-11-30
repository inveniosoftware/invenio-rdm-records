# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Software Heritage signals."""

from blinker import Namespace

_signals = Namespace()

post_publish_signal = _signals.signal("record-post-publish")
"""Signal to be sent after a record is published."""
