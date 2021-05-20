# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from marshmallow.exceptions import ValidationError


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(self, config, files_service=None, draft_files_service=None,
                 secret_links_service=None, pids_service=None):
        """Constructor for RecordService."""
        super().__init__(config, files_service, draft_files_service)
        self._secret_links = secret_links_service
        self._pids = pids_service

    #
    # Subservice
    #
    @property
    def secret_links(self):
        """Record secret link service."""
        return self._secret_links

    @property
    def pids(self):
        """Record pids service."""
        return self._pids
