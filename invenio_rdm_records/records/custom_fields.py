# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record has draft check field.

The HasDraftCheckField is used to check if an associated draft exists for a
a record.
"""

from flask import current_app
from werkzeug.local import LocalProxy

from invenio_records.systemfields.relations import (
    RelationsField,
    RelationBase,
    RelationsMapping,
)
from invenio_vocabularies.records.api import Vocabulary


class CustomFieldsRelation(RelationsField):
    """Relation field to manage custom fields."""

    def __init__(self):
        """Initialize the field."""
        super().__init__()
        self._fields = LocalProxy(lambda: self._load_custom_fields_relations())

    def _load_custom_fields_relations(self):
        cfs = current_app.config.get("RDM_RECORDS_CUSTOM_FIELDS", {})

        relations = {}
        for cf in cfs.values():
            if cf.relation_cls:
                relations[cf.name] = cf.relation_cls(
                    f"custom.{cf.name}",
                    keys=["title", "props", "icon"],
                    pid_field=Vocabulary.pid.with_type_ctx(cf.vocabulary_id),
                    cache_key=cf.vocabulary_id,
                )

        return relations

    def __set__(self, instance, values):
        """Setting the attribute."""
        raise ValueError("Cannot set this field directly.")


class MultiRelationsField(RelationsField):
    """Relations field for connections to external entities."""

    def __init__(self, **fields):
        """Initialize the field."""
        assert all(
            isinstance(f, RelationBase) or isinstance(f, RelationsField)
            for f in fields.values()
        )
        self._fields = {
            key: field
            for (key, field) in fields.items()
            if isinstance(field, RelationBase)
        }
        self._relation_fields = {
            key: field
            for (key, field) in fields.items()
            if isinstance(field, RelationsField)
        }

    def __getattr__(self, name):
        """Get a field definition."""
        if name in self._fields:
            return self._fields[name]

        raise AttributeError

    def __iter__(self):
        """Iterate over the configured fields."""
        return iter(getattr(self, f) for f in self._fields)

    def __contains__(self, name):
        """Return if a field exists in the configured fields."""
        return name in self._fields

    #
    # Helpers
    #
    def obj(self, instance):
        """Get the relations object."""
        # Check cache
        obj = self._get_cache(instance)
        if obj:
            return obj
        for relation_field in self._relation_fields.values():
            for (name, field) in relation_field._fields.items():
                if name not in self._fields:
                    self._fields[name] = field
        obj = RelationsMapping(record=instance, fields=self._fields)
        self._set_cache(instance, obj)
        return obj

    #
    # Data descriptor
    #
    def __get__(self, record, owner=None):
        """Accessing the attribute."""
        # Class access
        if record is None:
            return self
        return self.obj(record)

    def __set__(self, instance, values):
        """Setting the attribute."""
        obj = self.obj(instance)
        for k, v in values.items():
            setattr(obj, k, v)

    #
    # Record extension
    #
    def pre_commit(self, record):
        """Initialise the model field."""
        self.obj(record).validate()
        self.obj(record).clean()
