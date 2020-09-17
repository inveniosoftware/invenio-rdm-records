# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Error handling."""

from flask_resources.errors import HTTPJSONException, create_errormap_handler
from speaklater import _LazyString

handle_validation_error = create_errormap_handler(
    lambda exc: HTTPJSONValidationException(exc)
)


def unlazy_strings(obj):
    """Converts _LazyStrings in errors to Strings."""
    if isinstance(obj, _LazyString):
        return str(obj)
    elif isinstance(obj, list):
        return [unlazy_strings(o) for o in obj]
    elif isinstance(obj, dict):
        return {k: unlazy_strings(v) for k, v in obj.items()}
    else:
        return obj


class HTTPJSONValidationException(HTTPJSONException):
    """HTTP exception serializing to JSON and reflecting Marshmallow errors."""

    description = "A validation error occurred."

    def __init__(self, exception):
        """Constructor."""
        errors = exception.normalized_messages()  # dict
        super().__init__(code=400, errors=errors)

    def iter_errors_dict(self, message_node, prefix=''):
        """Recursively yield validation error dicts."""
        if isinstance(message_node, dict):
            for field, child in message_node.items():
                yield from self.iter_errors_dict(
                    child,
                    prefix=f"{prefix}.{field}" if prefix else f"{field}"
                )
        elif isinstance(message_node, list):
            # If the node is a list, it's a leaf node of str messages
            yield {
                "field": f"{prefix}",
                "messages": [str(m) for m in message_node]
            }
        else:
            # leaf node
            yield {
                "field": f"{prefix}",
                "messages": [str(message_node)]
            }

    def get_errors(self):
        """Get errors.

        :returns: List of dict representing the errors.
        """
        errors = list(self.iter_errors_dict(self.errors))
        # [
        #     e for e in
        # ]
        return errors
