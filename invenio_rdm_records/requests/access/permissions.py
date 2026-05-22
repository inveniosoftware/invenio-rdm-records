# SPDX-FileCopyrightText: 2023 TU Wien.
# SPDX-License-Identifier: MIT

"""Permissions-related definitions for access requests."""

from functools import partial

from flask_principal import Need

AccessRequestTokenNeed = partial(Need, "access_request_token")
AccessRequestTokenNeed.__doc__ = (
    "A need with the method preset to `'access_request_token'`."
)
