# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

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
