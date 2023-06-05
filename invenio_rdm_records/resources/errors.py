# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource errors."""

import json

from flask import g
from flask_resources import HTTPJSONException as _HTTPJSONException
from flask_resources.serializers.json import JSONEncoder


class HTTPJSONValidationWithMessageAsListException(_HTTPJSONException):
    """HTTP exception serializing to JSON where errors are in a list."""

    description = "A validation error occurred."

    def __init__(self, exception):
        """Constructor."""
        super().__init__(code=400, errors=exception.messages)


class HTTPJSONException(_HTTPJSONException):
    """HTTPJSONException that supports setting some extra body fields."""

    def __init__(self, code=None, errors=None, **kwargs):
        """Constructor."""
        description = kwargs.pop("description", None)
        response = kwargs.pop("response", None)
        super().__init__(code, errors, description=description, response=response)
        self._extra_fields = kwargs

    def get_body(self, environ=None, scope=None):
        """Get the response body."""
        body = {
            "status": self.code,
            "message": self.get_description(environ),
            **self._extra_fields,
        }

        errors = self.get_errors()
        if errors:
            body["errors"] = errors

        # TODO: Revisit how to integrate error monitoring services. See issue #56
        # Temporarily kept for expediency and backward-compatibility
        if self.code and (self.code >= 500) and hasattr(g, "sentry_event_id"):
            body["error_id"] = str(g.sentry_event_id)

        return json.dumps(body, cls=JSONEncoder)
