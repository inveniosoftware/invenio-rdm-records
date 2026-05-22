# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Permissions for Resource Access Token."""

from collections import namedtuple
from functools import partial

_Need = namedtuple(
    "Need", ["method", "signer_id", "pid_value", "file_key", "permission"]
)
RATNeed = partial(_Need, "rat")

"""
A Resource Access Tokens Need
ex: Need("3", "byy8e-7yz93", "file5.png", "write_file")
"""
