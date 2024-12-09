# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Errors for collections module."""


class CollectionError(Exception):
    """Base class for collection errors."""


class CollectionNotFound(CollectionError):
    """Collection not found error."""


class CollectionTreeNotFound(CollectionError):
    """Collection tree not found error."""


class InvalidQuery(CollectionError):
    """Query syntax is invalid."""


class LogoNotFoundError(CollectionError):
    """Logo not found error."""
