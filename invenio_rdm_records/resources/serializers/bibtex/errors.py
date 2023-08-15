# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BibTex Errors."""


class MissingRequiredFieldError(Exception):
    """Base class.

    The exception should be raised when the specific,
    required field doesn't exist in the record.
    """

    def _init_(self, field):
        self.field = field

    def _str_(self):
        return "Missing field: " + self.field
