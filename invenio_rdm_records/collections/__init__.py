# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections entrypoint."""

from .models import Collection, CollectionTree
from .searchapp import search_app_context

__all__ = (
    "Collection",
    "CollectionTree",
    "search_app_context",
)
