# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields registry."""

# TODO: Evaluate creating a base registry class, since we use almost the same
# implementation for services, indexers and now custom fields.

from marshmallow import Schema
from .text import TextCF


class CustomFieldsRegistry:
    """Custom Fields registry."""

    def __init__(self):
        """Initialize the registry."""
        self._cfs = {
            # FIXME: should be prepend with `custom`
            # see below in register().
            # name is duplicated...
            "experiment": TextCF(name="experiment"),
        }

    def register(self, field_key, field_type):
        """Register a new custom field instance."""
        # TODO: How do we register? read from config?
        # reading from config needs to be lazy, since vocabularies
        # will need app context to be loaded.

        # TODO: registering should prepend the `custom` to the field name.
        self._cfs[field_key] = field_type

    def get(self, field_name):
        """Get an custom field given its name."""
        # TODO: Should field name have the prefix?
        # who should be responsible for this prefixing?
        # service (set it in config)?
        return self._cfs[field_name]

    def all(self):
        """Get all the registered custom fields."""
        return self._cfs

    def to_schema(self):
        """Create a marshmallow schema from all registered custom fields."""
        schema_dict = {
            field_key: field.schema() for field_key, field in self.all().items()
        }
        return Schema.from_dict(schema_dict)