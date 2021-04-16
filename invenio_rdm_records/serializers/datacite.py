# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite based serializers for Invenio RDM Records."""

from flask_resources.serializers import SerializerMixin


class RDMDataCite43Serializer(SerializerMixin):
    """Marshmallow based DataCite serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def serialize_object(self, obj, response_ctx=None, *args, **kwargs):
        """Dump the object into an XML string."""
        # PIDS-FIXME: implement using datacite.schema43
        return {}

    def serialize_object_list(
        self, obj_list, response_ctx=None, *args, **kwargs
    ):
        """Dump the object list into an XML string.

        :param: obj_list an IdentifiedRecords object
        """
        raise NotImplementedError()
