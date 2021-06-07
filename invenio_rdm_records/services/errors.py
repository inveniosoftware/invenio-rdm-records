# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service Errors."""


class RDMRecordsException(Exception):
    """Base exception for RDMRecords errors."""


class EmbargoNotLiftedError(RDMRecordsException):
    """Embargo could not be lifted ."""

    def __init__(self, record_id):
        """Initialise error."""
        super().__init__(
            f"Embargo could not be lifted for record: {record_id}"
        )
