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

from invenio_records.systemfields.relations import RelationBase
from invenio_vocabularies.records.api import Vocabulary


class CustomFieldsRelation(RelationBase):
    """Relation field to manage custom fields."""

    def __init__(self):
        """Initialize the field."""
        super().__init__()
        self._fields = LocalProxy(
            lambda: self._load_custom_fields_relations()
        )

    def _load_custom_fields_relations(self):

        cfs = current_app.config.get("RDM_RECORDS_CUSTOM_FIELDS", {})

        relations = {}
        for cf in cfs.values():
            # FIXME: how to abstract this so relation_cls is not present in BaseCF
            if cf.relation_cls:
                relations[cf.name] = cf.relation_cls(
                f"custom.{cf.name}",
                keys=["title", "props", "icon"],
                pid_field=Vocabulary.pid.with_type_ctx(cf.vocabulary_id),
                cache_key=cf.vocabulary_id,
            )

        return relations
