# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from flask.helpers import make_response
from flask.wrappers import Response
from flask_resources import ResponseHandler

class CitationResponseHandler(ResponseHandler):
    def make_response(self, obj_or_list, style, location, code, many=False):
        """Builds a response for one object."""
        # If view returns a response, bypass the serialization.
        breakpoint()
        if isinstance(obj_or_list, Response):
            return obj_or_list

        # https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response
        # (body, status, header)
        if many:
            serialize = self.serializer.serialize_object_list
        else:
            serialize = self.serializer.serialize_object

        return make_response(
            "" if obj_or_list is None else serialize(obj_or_list, style,
                                                     location),
            code,
            self.make_headers(obj_or_list, code, many=many),
        )
