# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Secret links service API."""

from copy import deepcopy

from invenio_db import db
from invenio_files_rest.errors import FileSizeError
from invenio_files_rest.models import ObjectVersion

from ..base.links import LinksTemplate
from ..records.schema import ServiceSchemaWrapper


class RecordAcces:
    """A mixin class to extend the records service with secret links support."""


    def __init__(self, config, records_service):
        self.config = config


service.access.create_secret_link

serivce.files.ini

