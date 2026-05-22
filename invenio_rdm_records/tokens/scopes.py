# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

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
