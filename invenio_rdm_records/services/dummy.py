# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dummy services for expandable entities that don't have a real service."""


class DummyResultList:
    """Dummy result item list."""

    def __init__(self, hits):
        """Constructor."""
        self.hits = hits


class DummyExpandingService:
    """A dummy service for entity expansion that doesn't perform any real actions.

    This dummy service can be used for making entities expandable which do not have
    a proper service backing them, by providing dummy implementations of some methods.
    """

    def __init__(self, type):
        """Constructor."""
        self._type = type

    def read(self, identity, id_, **kwargs):
        """Perform a dummy read operation for the given ID."""
        return {self._type: id_}

    def read_many(self, identity, ids):
        """Create a dummy result list for all IDs."""
        return DummyResultList([{self._type: value, "id": value} for value in ids])
