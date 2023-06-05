# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions-related definitions for access requests."""

from functools import partial

from flask_principal import Need

AccessRequestTokenNeed = partial(Need, "access_request_token")
AccessRequestTokenNeed.__doc__ = (
    "A need with the method preset to `'access_request_token'`."
)
