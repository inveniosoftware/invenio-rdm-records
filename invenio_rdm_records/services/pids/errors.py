# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record PIDs Service Errors."""


from ..errors import RDMRecordsException


class PIDTypeNotSupportedError(RDMRecordsException):
    """One or more PID type is not supported by the system."""

    def __init__(self, pid_types):
        """Initialise error."""
        super().__init__(
            f"No configuration defined for PIDs {pid_types}"
        )


class ProviderNotSupportedError(RDMRecordsException):
    """One or more PID type is not supported by the system."""

    def __init__(self, provider, scheme):
        """Initialise error."""
        super().__init__(
            f"Unknown PID provider {provider} for {scheme}"
        )
