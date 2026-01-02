# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource access tokens module errors."""

from invenio_i18n import _
from invenio_rest.errors import RESTException


class ResourceAccessTokenError(RESTException):
    """Resource access token base error class."""

    code = 400


class MissingTokenIDError(ResourceAccessTokenError):
    """Resource access token error for missing token ID."""

    description = _(
        'Missing "kid" key with personal access token ID in JWT header of '
        "resource access token."
    )


class InvalidTokenIDError(ResourceAccessTokenError):
    """Resource access token error for invalid token ID."""

    description = _(
        '"kid" JWT header value of resource access token not a valid personal '
        "access token ID."
    )


class TokenDecodeError(ResourceAccessTokenError):
    """Resource access token error for token decoding errors."""

    description = _("Failed to decode resource access token.")


class InvalidTokenError(ResourceAccessTokenError):
    """Resource access token error for invalid token."""

    description = _("The resource access token is invalid.")


class InvalidTokenSubjectError(ResourceAccessTokenError):
    """Resource access token error for invalid subject of a token."""

    description = _("The resource access token subject is invalid.")


class ExpiredTokenError(InvalidTokenError):
    """Resource access token error for expired token."""

    description = _("The resource access token is expired.")


class RATFeatureDisabledError(ResourceAccessTokenError):
    """Resource access token error for disabled feature."""

    description = _("Resource Access Tokens feature is currently disabled.")
