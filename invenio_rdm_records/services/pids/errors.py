# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record PIDs Service Errors."""

from invenio_i18n import lazy_gettext as _

from ..errors import RDMRecordsException


class PIDSchemeNotSupportedError(RDMRecordsException):
    """One or more PID schemes is not supported by the system."""

    def __init__(self, schemes):
        """Initialise error."""
        super().__init__(
            _("No configuration defined for PIDs {schemes}".format(schemes=schemes))
        )


class ProviderNotSupportedError(RDMRecordsException):
    """Provider not supported by the system."""

    def __init__(self, provider, scheme):
        """Initialise error."""
        super().__init__(
            _(
                "Unknown PID provider %(provider)s for %(scheme)s",
                provider=provider,
                scheme=scheme,
            )
        )
