# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource errors."""


from flask_resources import HTTPJSONException


class HTTPJSONValidationWithMessageAsListException(HTTPJSONException):
    """HTTP exception serializing to JSON where errors are in a list."""

    description = "A validation error occurred."

    def __init__(self, exception):
        """Constructor."""
        super().__init__(code=400, errors=exception.messages)
