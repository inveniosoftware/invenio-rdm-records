# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM user moderation action."""


def on_block(user_id, uow=None, **kwargs):
    """Removes records that belong to a user."""
    pass


def on_restore(user_id, uow=None, **kwargs):
    """Restores records that belong to a user."""
    pass
