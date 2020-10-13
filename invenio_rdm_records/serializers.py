# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

import json

from flask_resources.serializers import JSONSerializer


class UIJSONSerializer(JSONSerializer):
    """UI JSON serializer implementation."""

    def _serialize_access_right(self, obj):
        """Dump ui config for `access_right` field."""
        return dict(
            access_right=dict(
                category=obj["access"]["access_right"]
            ))

    def serialize_object(self, obj, response_ctx=None, *args, **kwargs):
        """Dump the object into a json string."""
        obj['ui'] = self._serialize_access_right(obj)
        return json.dumps(obj)

    def serialize_object_list(
            self, obj_list, response_ctx=None, *args, **kwargs):
        """Dump the object list into a json string."""
        for obj in obj_list["hits"]["hits"]:
            obj['ui'] = self._serialize_access_right(obj)
        return json.dumps(obj_list)
