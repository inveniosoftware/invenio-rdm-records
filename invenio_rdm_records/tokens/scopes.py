# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth2 tokens scopes."""

from invenio_i18n import lazy_gettext as _
from invenio_oauth2server.models import Scope

tokens_generate_scope = Scope(
    id_="tokens:generate",
    group="tokens",
    help_text=_("Allow generation of granular access JWT tokens."),
    internal=True,
)
"""Allow generation of granular access JWT tokens."""
