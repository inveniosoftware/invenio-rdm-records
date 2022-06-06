# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record PIDs Service Errors."""


from ..errors import RDMRecordsException


class PIDSchemeNotSupportedError(RDMRecordsException):
    """One or more PID schemes is not supported by the system."""

    def __init__(self, schemes):
        """Initialise error."""
        super().__init__(f"No configuration defined for PIDs {schemes}")


class ProviderNotSupportedError(RDMRecordsException):
    """Provider not supported by the system."""

    def __init__(self, provider, scheme):
        """Initialise error."""
        super().__init__(f"Unknown PID provider {provider} for {scheme}")
