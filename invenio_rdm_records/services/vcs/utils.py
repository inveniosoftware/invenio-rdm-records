# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Utility functions."""

from invenio_pidstore.models import PersistentIdentifier


def retrieve_recid_by_uuid(rec_uuid):
    """Retrieves a persistent identifier given its objects uuid.

    Helper function.
    """
    recid = PersistentIdentifier.get_by_object(
        pid_type="recid",
        object_uuid=rec_uuid,
        object_type="rec",
    )
    return recid
