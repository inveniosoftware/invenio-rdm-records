# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields sub service for InvenioRDM."""

from elasticsearch.exceptions import RequestError
from invenio_drafts_resources.services.records import RecordService

from invenio_rdm_records.proxies import current_custom_fields_registry as cf_registry


class CustomFieldsService(RecordService):
    """Custom Fields service."""

    def create(self, fields_name):
        """Create custom fields."""

        fields = []

        if fields_name:
            for field_name in fields_name:
                fields.append(cf_registry.get(field_name))
        else:
            fields = cf_registry.all().values()

        # this means we do not have to choose a write index
        # we update only the latest mapping/alias
        index = self.record_cls.index

        properties = {}
        for field in fields:
            # TODO: custom is binded to json schema. Do we define config to control it?
            properties[f"custom.{field.name}"] = field.mapping

        try:
            res = index.put_mapping(body={"properties": properties})
        except RequestError as e:
            return False, e.info["error"]["reason"]

        return res.get("acknowledged"), None

    def exists(self, field_name):
        """Check if a custom field exists."""
        # TODO: creating an `is_registered` method makes sense?
        # to check if it is "configured" or not.
        # while this method checks existance in ES, or should it do both?
        index = self.record_cls.index

        # FIXME: get_mapping returns a dict with the index as key
        # we have in index._name the alias, so we cannot access the actual value
        # assume is only one mapping returned
        mapping = list(index.get_mapping().values())[0]["mappings"]

        parts = field_name.split(".")
        for part in parts:
            mapping = mapping["properties"]  # here to avoid last field access
            if part not in mapping.keys():
                return False

            mapping = mapping[part]

        return True
