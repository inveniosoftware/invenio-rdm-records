# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

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
