# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM services decorators."""

from functools import wraps

from flask import current_app
from invenio_records_resources.services.errors import PermissionDeniedError


def groups_enabled(group_subject_type, **kwargs):
    """Decorator to check if users are trying to access disabled feature."""

    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            subject_type = kwargs["subject_type"]
            if (
                not current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)
                and subject_type == group_subject_type
            ):
                raise PermissionDeniedError()

            return f(self, *args, **kwargs)

        return inner

    return decorator
