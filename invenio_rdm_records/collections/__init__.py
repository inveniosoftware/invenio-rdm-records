# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections entrypoint."""

from .errors import CollectionNotFound, CollectionTreeNotFound, LogoNotFoundError
from .models import Collection, CollectionTree
from .searchapp import search_app_context

__all__ = (
    "Collection",
    "CollectionNotFound",
    "CollectionTree",
    "CollectionTreeNotFound",
    "LogoNotFoundError",
    "search_app_context",
)
