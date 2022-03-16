# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Unit of work operations for OAI-PMH services."""

from invenio_db import db
from invenio_records_resources.services.uow import Operation


class OAISetCommitOp(Operation):
    """OAI-PMH set add/update operation."""

    def __init__(self, oai_set):
        """Initialize the set commit operation."""
        super().__init__()
        self._oai_set = oai_set

    def on_register(self, uow):
        """Add set to db session."""
        db.session.add(self._oai_set)


class OAISetDeleteOp(Operation):
    """OAI-PMH set delete operation."""

    def __init__(self, oai_set):
        """Initialize the set delete operation."""
        super().__init__()
        self._oai_set = oai_set

    def on_register(self, uow):
        """Hard delete set."""
        db.session.delete(self._oai_set)
