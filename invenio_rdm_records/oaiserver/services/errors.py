# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022-2023 Graz University of Technology.
# Copyright (C) 2026 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for OAIPMH-Set."""

from invenio_i18n import gettext as _


class OAIPMHError(Exception):
    """Base class for OAI-PMH errors."""

    def __init__(self, description, *args: object):
        """Constructor."""
        self.description = description
        super().__init__(*args)


class OAIPMHSetDoesNotExistError(OAIPMHError):
    """The provided set spec does not exist."""

    def __init__(self, query_arguments):
        """Initialise error."""
        super().__init__(
            description=_(
                "A set where %(query_arguments)s does not exist.",
                query_arguments=query_arguments,
            )
        )


class OAIPMHSetIDDoesNotExistError(OAIPMHError):
    """The provided set spec does not exist."""

    def __init__(self, id):
        """Initialise error."""
        super().__init__(description=_("A set with id %(id)s does not exist.", id=id))


class OAIPMHSetSpecAlreadyExistsError(OAIPMHError):
    """The provided set spec already exists."""

    def __init__(self, spec):
        """Initialise error."""
        super().__init__(
            description=_("A set with spec '%(spec)s' already exists.", spec=spec)
        )


class OAIPMHSetNotEditable(OAIPMHError):
    """The provided set is not editable."""

    def __init__(self, id):
        """Initialise error."""
        super().__init__(
            description=_("The set with id %(id)s is not editable.", id=id)
        )
